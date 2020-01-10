from datetime import timedelta


class Issue(object):
    """Класс для работы с отдельной задачей."""

    def __init__(self, jira_issue, parent):
        """Инициализация объекта для хранения данных по задаче.

        Args:
            jira_issue: Информация по задаче из АПИ.
            parent: Объект-родитель задачи.
        """
        self._parent = parent
        self.id = jira_issue.id
        self.issue_id = jira_issue.key
        self.summary = jira_issue.fields.summary.lstrip().rstrip()
        self.type = jira_issue.fields.issuetype
        self.components = getattr(jira_issue.fields, 'components', None)
        self.assignee = getattr(jira_issue.fields, 'assignee', '')
        self.worklog = getattr(jira_issue.fields, 'worklog', None)
        self.worklog_max_results = self.worklog.maxResults if self.worklog is not None else 0
        self.worklog_total = self.worklog.total if self.worklog is not None else 0
        self._subtasks = []
        self.timespent = timedelta()
        self.timespent_by_author = {}

        if getattr(jira_issue.fields, 'subtasks', None) is not None:
            self.add_subtasks(subtasks=jira_issue.fields.subtasks)

        if self.components:
            self.components = ','.join([c.name for c in self.components])

    @property
    def subtasks(self):
        return self._subtasks

    def add_subtasks(self, subtasks):
        """Добавление подзадач к задаче, если они существуют."""
        for task in subtasks:
            self._subtasks.append(Issue(jira_issue=task, parent=self))

    def calc_timespent(self, worklogs):
        """Подсчитать внесенное в задачу время."""
        seconds = [w.timeSpentSeconds for w in worklogs]
        self.timespent += timedelta(seconds=sum(seconds))
        if isinstance(self._parent, Issue):
            self._parent.timespent += self.timespent

    def calc_timespent_by_author(self, worklogs):
        """Подсчитать внесенное в задачу время для каждого пользователя отдельно."""
        for w in worklogs:
            if self.timespent_by_author.get(w.author.name) is None:
                self.timespent_by_author[w.author.name] = timedelta(seconds=w.timeSpentSeconds)
            else:
                self.timespent_by_author[w.author.name] += timedelta(seconds=w.timeSpentSeconds)
