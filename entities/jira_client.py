from pathlib import Path
from jira import JIRA
from pandas import DataFrame

from entities.issues import Issues


class JiraClient(object):

    def __init__(self, host, login, password):
        self.host = host
        self.basic_auth = (login, password)
        self.jira = JIRA(server=self.host, basic_auth=self.basic_auth)

        self.issues = Issues(connection=self.jira)

    def worklogs_to_excel(self, filename, sheet, jql, startrow=0, startcol=0):
        columns = {'issue': [], 'summary': [], 'timespent': [], 'query': [jql]}
        for issues_list in self.issues.issues.values():
            for issue in issues_list:
                columns['issue'].append(issue.issue_id)
                columns['summary'].append(issue.summary)
                columns['timespent'].append(str(issue.timespent))
        columns['query'].extend([None for _ in range(startrow + len(columns['issue']) - 1)])

        df = DataFrame(data=columns)
        filename = str(Path(__file__).parent.parent.absolute()) + '\\' + filename + '.xlsx'
        df.to_excel(excel_writer=filename, sheet_name=sheet, index=False,
                    startrow=startrow, startcol=startcol)

        print('Сохраено в ' + filename)

    def close_connection(self):
        print('Закрытие сессии Jira')
        self.jira.close()
