import os

from entities.excel_tables.excel_table import ExcelTable


class WorklogsTable(ExcelTable):
    """Класс для создания таблицы с собранными ворклогами."""

    COLUMNS = ['type',
               'components',
               'issue',
               'summary',
               'timespent(min)',
               'timespent(hours)',
               'timespent(by author)',
               'assignee',
               'query']
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
        self.get('assignee').append(issue.assignee)
        self.get('timespent(min)').append(self.jira_client.sec_to_mins(s=issue.timespent.total_seconds()))
        self.get('timespent(hours)').append(self.jira_client.sec_to_hours_mins(s=issue.timespent.total_seconds()))
        self.get('timespent(by author)').append('')
        for key, value in issue.timespent_by_author.items():
            self.get('timespent(by author)')[-1] += key + ' ' + str(
                self.jira_client.sec_to_hours_mins(s=value.total_seconds())) + '\n'

    def insert_jql_into_table(self, jql):
        """Добавление текущего JQL запроса в таблицу."""
        self.get('query').append(jql)
        self.get('query').extend([None for _ in range(len(self.get('issue')) - 1)])
