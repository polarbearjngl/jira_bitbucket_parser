from entities.jira.worklog_by import WorklogBy


class WorklogByIssueForAuthor(WorklogBy):

    def __init__(self, issue, author):
        super().__init__()
        self.author = author
        self.issue_id = issue.issue_id
        self.summary = issue.summary
        self.type = issue.type
        self.components = issue.components
        self.assignee = issue.assignee
