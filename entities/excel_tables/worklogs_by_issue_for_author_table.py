import os

from entities.excel_tables.excel_table import ExcelTable


class WorklogsByIssueForAuthorTable(ExcelTable):
    """Класс для создания таблицы с собранными ворклогами по каждой задаче отдельно."""

    COLUMNS = ['type',
               'components',
               'issue',
               'summary',
               'author',
               'timespent(min)',
               'timespent(hours)',
               'comments',
               'assignee']
    DIR_NAME = 'worklogs' + os.sep

    def __init__(self, jira_client, **kwargs):
        super().__init__(**kwargs)
        self.jira_client = jira_client
        for key in self.COLUMNS:
            setattr(self, key, [])

    def insert_data_for_issue_into_table(self, issue):
        """Запись  данных по задаче в соответствующие ячейки."""
        self.get('type').append(issue.type)
        self.get('components').append(issue.components)
        self.get('issue').append(issue.issue_id)
        self.get('summary').append(issue.summary)
        self.get('author').append(issue.author)
        self.get('assignee').append(issue.assignee)
        self.get('comments').append(issue.worklog_comments)
        self.get('timespent(min)').append(issue.timespent_min)
        self.get('timespent(hours)').append(issue.timespent_hours)
