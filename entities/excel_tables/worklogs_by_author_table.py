import os

from entities.excel_tables.excel_table import ExcelTable


class WorklogsByAuthorTable(ExcelTable):
    COLUMNS = ['author',
               'issues count',
               'timespent(min)',
               'timespent(hours)',
               'average(min)',
               'average(hours)',
               'components',
               'summaries',
               'issues']
    DIR_NAME = 'worklogs' + os.sep

    def __init__(self, jira_client, **kwargs):
        super().__init__(**kwargs)
        self.jira_client = jira_client
        for key in self.COLUMNS:
            setattr(self, key, [])

    def insert_data_for_author_into_table(self, by_author):
        self.get('author').append(by_author.author)
        self.get('issues count').append(len(by_author.issue_ids))
        self.get('timespent(min)').append(by_author.timespent_min)
        self.get('timespent(hours)').append(by_author.timespent_hours)
        if len(by_author.issue_ids) > 0:
            average_min = float('{0:.2f}'.format(by_author.timespent_min / len(by_author.issue_ids)))
            average_hours = float('{0:.2f}'.format(by_author.timespent_hours / len(by_author.issue_ids)))
        else:
            average_min = average_hours = 0
        self.get('average(min)').append(average_min)
        self.get('average(hours)').append(average_hours)
        self.get('components').append(by_author.components)
        self.get('summaries').append(by_author.summaries)
        self.get('issues').append(by_author.issues)
