from pathlib import Path
from jira import JIRA
from pandas import DataFrame
import os
from entities.issues import Issues


class JiraClient(object):

    def __init__(self, host, login, password):
        self.host = host
        self.basic_auth = (login, password)
        self.jira = JIRA(server=self.host, basic_auth=self.basic_auth)

        self.issues = Issues(connection=self.jira)

    def worklogs_to_excel(self, filename, sheet, jql, startrow=0, startcol=0):
        columns = {'issue': [],
                   'summary': [],
                   'timespent': [],
                   'timespent by author': [],
                   'query': [jql]}
        columns = self.generate_table(columns=columns, startrow=startrow)

        directory = str(Path(__file__).parent.parent.absolute()) + '\\reports\\'
        filename = directory + filename + '.xlsx'
        if not os.path.exists(directory):
            os.makedirs(directory)

        df = DataFrame(data=columns)
        df.to_excel(excel_writer=filename, sheet_name=sheet, index=False,
                    startrow=startrow, startcol=startcol)

        print('Сохранено в ' + filename)

    def generate_table(self, columns, startrow):
        for issues_list in self.issues.all_issues.values():
            for issue in issues_list:
                columns['issue'].append(issue.issue_id)
                columns['summary'].append(issue.summary)
                columns['timespent'].append(self.sec_to_hours(s=issue.timespent.total_seconds()))
                columns['timespent by author'].append('')
                for key, value in issue.timespent_by_author.items():
                    columns['timespent by author'][-1] += key + ' ' + self.sec_to_hours(s=value.total_seconds()) + '\n'

        columns['query'].extend([None for _ in range(startrow + len(columns['issue']) - 1)])
        return columns

    @staticmethod
    def sec_to_hours(s):
        hours = str(s // 3600)[:-2]
        mins = str((s % 3600) // 60)[:-2]
        return "{}h {}m".format(hours, mins)

    def close_connection(self):
        print('Закрытие сессии Jira')
        self.jira.close()
