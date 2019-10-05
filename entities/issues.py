from datetime import timedelta


class Issues(object):

    def __init__(self, connection):
        self.jira = connection
        self.issues = {}

    def search_issues(self, jql, fields='issue,key,summary,subtasks'):
        issues_list = self.jira.search_issues(jql_str=jql,
                                              maxResults=False,
                                              fields=fields)
        self.issues[jql] = [Issue(jira_issue=issue, parent=self) for issue in issues_list]
        print('По данному запросу найдено %s задач' % len(self.issues[jql]))
        return self.issues[jql]

    def collect_worklogs(self):
        sub_tasks_count, tasks_count = 0, 0
        for issues_list in self.issues.values():
            for task in issues_list:
                tasks_count += 1
                for _ in task.subtasks:
                    sub_tasks_count += 1

        print('Начат сбор ворклогов в %s подзадачах для %s задач' % (sub_tasks_count, tasks_count))

        for issues_list in self.issues.values():
            for task in issues_list:
                for subtask in task.subtasks:
                    issue = self.jira.issue(id=subtask.id)
                    worklogs = issue.fields.worklog.worklogs
                    time_spent_seconds = [w.timeSpentSeconds for w in worklogs]
                    subtask.calc_timespent(seconds=time_spent_seconds)

        print('Закончен сбор ворклогов')


class Issue(object):

    def __init__(self, jira_issue, parent):
        self._parent = parent
        self.id = jira_issue.id
        self.issue_id = jira_issue.key
        self.summary = jira_issue.fields.summary
        self._subtasks = []
        self.timespent = timedelta()

        if getattr(jira_issue.fields, 'subtasks', None) is not None:
            self.add_subtasks(subtasks=jira_issue.fields.subtasks)

    @property
    def subtasks(self):
        return self._subtasks

    def add_subtasks(self, subtasks):
        for task in subtasks:
            self._subtasks.append(Issue(jira_issue=task, parent=self))

    def calc_timespent(self, seconds):
        self.timespent += timedelta(seconds=sum(seconds))
        if isinstance(self._parent, Issue):
            self._parent.timespent += self.timespent
