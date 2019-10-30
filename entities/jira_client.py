import os
from pathlib import Path
from jira import JIRA

from entities.excel_tables import WorklogsTable, WorklogsByAuthorTable
from entities.issues import Issues
import platform


class JiraClient(object):
    """Класс клиента для работы с джирой."""

    def __init__(self, host, login, password):
        self.host = host
        self.basic_auth = (login, password)
        self.jira = JIRA(server=self.host, basic_auth=self.basic_auth)

        self.issues = Issues(connection=self.jira)

    def search_issues(self, jql):
        """Поиск задач в джира, подходящих под заданный jql запрос."""
        return self.issues.search_issues(jql=self.decode_query(query=jql))

    def worklogs_to_excel(self, filename, jql, startrow=0, startcol=0):
        """Запись собранных ворклогов в эксель файл.

        Args:
            filename: Наименование файла с отчетом.
            jql: Текст запроса, для результатов которого необходимо записать ворклоги.
            startrow: Номер левого ряда для таблицы.
            startcol: Номер левой строки для таблицы.

        """
        worklogs_table = WorklogsTable(jira_client=self)
        for issues_list in self.issues.all_issues.values():
            for issue in issues_list:
                worklogs_table.insert_data_for_issue_into_table(issue=issue)
        worklogs_table.insert_jql_into_table(jql=self.decode_query(query=jql))

        worklogs_by_author_table = WorklogsByAuthorTable(jira_client=self)
        for info in self.issues.worklogs_by_author.by_author.values():
            worklogs_by_author_table.insert_data_for_author_into_table(by_author=info)

        directory = str(Path(__file__).parent.parent.absolute()) + os.sep + 'reports' + os.sep

        worklogs_table.to_excel(directory=directory,
                                filename=filename,
                                startrow=startrow, startcol=startcol, sheet_name='Worklogs')

        worklogs_by_author_table.to_excel(directory=directory,
                                          filename=filename,
                                          startrow=startrow, startcol=startcol, sheet_name='WorklogsByAuthor')


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

    def decode_query(self, query):
        if platform.system() == 'Windows':
            for encode, decode in [['cp866', 'utf-8'], ['cp1251', 'utf-8'], ['cp866', 'cp1251']]:
                decoded_query = self.try_decode(string=query, encode=encode, decode=decode)
                if decoded_query is not None:
                    return decoded_query
        return query

    @staticmethod
    def try_decode(string, encode, decode, exceptions=(UnicodeEncodeError, UnicodeDecodeError)):
        try:
            return string.encode(encode).decode(decode)
        except exceptions:
            return None

    def close_connection(self):
        print('Закрытие сессии Jira')
        self.jira.close()
