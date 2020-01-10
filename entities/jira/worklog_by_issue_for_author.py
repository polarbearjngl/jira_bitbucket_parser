from entities.jira.worklog_by import WorklogBy


class WorklogByIssueForAuthor(WorklogBy):
    """Класс для работы с записью по ворклогу для задачи для каждого автора ворклога по отдельности."""

    def __init__(self, issue, author, worklog_comments):
        """Инициализация

        Args:
            issue: Объект Issue.
            author: Автор ворклога.
            worklog_comments: Комментарии для ворклога.
        """
        super().__init__()
        self.author = author
        self.issue_id = issue.issue_id
        self.summary = issue.summary
        self.type = issue.type
        self.components = issue.components
        self.assignee = issue.assignee
        self.worklog_comments = worklog_comments
