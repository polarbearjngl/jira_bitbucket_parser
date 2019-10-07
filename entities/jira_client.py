from pathlib import Path
from jira import JIRA
from pandas import DataFrame
import os
from entities.issues import Issues


class JiraClient(object):
    """Класс клиента для работы с джирой."""

    def __init__(self, host, login, password):
        self.host = host
        self.basic_auth = (login, password)
        self.jira = JIRA(server=self.host, basic_auth=self.basic_auth)

        self.issues = Issues(connection=self.jira)

    def worklogs_to_excel(self, filename, sheet, jql, startrow=0, startcol=0):
        """Запись собранных ворклогов в эксель файл.

        Args:
            filename: Наименование файла с отчетом.
            sheet: Наименование листа, в который необходимо записать отчет.
            jql: Текст запроса, для результатов которого необходимо записать ворклоги.
            startrow: Номер левого ряда для таблицы.
            startcol: Номер левой строки для таблицы.

        """
        columns = {'issue': [],
                   'summary': [],
                   'timespent(min)': [],
                   'timespent(hours)': [],
                   'timespent(by author)': [],
                   'query': [jql]}
        columns = self.generate_table(columns=columns)

        directory = str(Path(__file__).parent.parent.absolute()) + '\\reports\\'
        filename = directory + filename + '.xlsx'
        if not os.path.exists(directory):
            os.makedirs(directory)

        df = DataFrame(data=columns)
        df.to_excel(excel_writer=filename, sheet_name=sheet, index=False,
                    startrow=startrow, startcol=startcol)

        print('Сохранено в ' + filename)

    def generate_table(self, columns):
        """Заполнение тбалицы с заданными колонками."""
        for issues_list in self.issues.all_issues.values():
            for issue in issues_list:
                columns['issue'].append(issue.issue_id)
                columns['summary'].append(issue.summary)
                columns['timespent(min)'].append(self.sec_to_mins(s=issue.timespent.total_seconds()))
                columns['timespent(hours)'].append(self.sec_to_hours_mins(s=issue.timespent.total_seconds()))
                columns['timespent(by author)'].append('')
                for key, value in issue.timespent_by_author.items():
                    columns['timespent(by author)'][-1] += key + ' ' + str(self.sec_to_hours_mins(s=value.total_seconds())) + '\n'

        columns['query'].extend([None for _ in range(len(columns['issue']) - 1)])
        return columns

    @staticmethod
    def sec_to_hours_mins(s):
        hours = int(s // 3600)
        mins = (s % 3600) // 60
        if mins == 0:
            return hours
        else:
            mins = str(mins / 60)[2:]
            return "{},{}".format(hours, mins)

    @staticmethod
    def sec_to_mins(s):
        return int(str(s // 60)[:-2])

    def close_connection(self):
        print('Закрытие сессии Jira')
        self.jira.close()
