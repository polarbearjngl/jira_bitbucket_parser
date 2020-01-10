from entities.jira.worklog_by import WorklogBy
from entities.jira.worklog_by_issue_for_author import WorklogByIssueForAuthor


class WorklogByAuthor(WorklogBy):
    """Информация по ворклогам для автора."""

    def __init__(self, author):
        """Создание новой строки для автора ворклога по его имени

        Args:
            author: Имя автора ворклога.
        """
        super().__init__()
        self.author = author
        self.issue_ids = []
        self.components = ''
        self.summaries = ''
        self.issues = ''
        self.worklogs_by_issue = {}

    def update_worklogs_by_issue(self, issue, seconds):
        if self.worklogs_by_issue.get(issue) is None:
            self.worklogs_by_issue.update({issue: WorklogByIssueForAuthor(issue=issue, author=self.author)})

        self.worklogs_by_issue[issue].update_timespent(seconds=seconds)
