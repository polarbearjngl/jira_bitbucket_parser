from datetime import timedelta


class Issues(object):

    def __init__(self, connection):
        self.jira = connection
        self.all_issues = {}

    def search_issues(self, jql, fields='issue,key,summary,subtasks,worklog'):
        issues_list = self.jira.search_issues(jql_str=jql,
                                              maxResults=False,
                                              fields=fields,
                                              expand='worklog')
        self.all_issues[jql] = [Issue(jira_issue=issue, parent=self) for issue in issues_list]
        print('По данному запросу найдено %s задач' % len(self.all_issues[jql]))
        return self.all_issues[jql]

    def collect_worklogs(self):
        sub_tasks_count, tasks_count = 0, 0
        for issues_list in self.all_issues.values():
            for task in issues_list:
                tasks_count += 1
                for _ in task.subtasks:
                    sub_tasks_count += 1

        print('Начат сбор ворклогов для %s подзадач и %s задач' % (sub_tasks_count, tasks_count))

        for issues_list in self.all_issues.values():
            for task in issues_list:
                if task.worklog is not None:
                    if task.worklog_max_results < task.worklog_total:
                        task_worklogs = self.jira.worklogs(issue=task.id)
                    else:
                        task_worklogs = task.worklog.worklogs
                    task.calc_timespent(worklogs=task_worklogs)
                    task.calc_timespent_by_author(worklogs=task_worklogs)

                for subtask in task.subtasks:
                    subtask_worklogs = self.jira.worklogs(issue=subtask.id)
                    subtask.calc_timespent(worklogs=subtask_worklogs)
                    task.calc_timespent_by_author(worklogs=subtask_worklogs)
        print('Закончен сбор ворклогов')


class Issue(object):

    def __init__(self, jira_issue, parent):
        self._parent = parent
        self.id = jira_issue.id
        self.issue_id = jira_issue.key
        self.summary = jira_issue.fields.summary
        self.worklog = getattr(jira_issue.fields, 'worklog', None)
        self.worklog_max_results = self.worklog.maxResults if self.worklog is not None else 0
        self.worklog_total = self.worklog.total if self.worklog is not None else 0
        self._subtasks = []
        self.timespent = timedelta()
        self.timespent_by_author = {}

        if getattr(jira_issue.fields, 'subtasks', None) is not None:
            self.add_subtasks(subtasks=jira_issue.fields.subtasks)

    @property
    def subtasks(self):
        return self._subtasks

    def add_subtasks(self, subtasks):
        for task in subtasks:
            self._subtasks.append(Issue(jira_issue=task, parent=self))

    def calc_timespent(self, worklogs):
        seconds = [w.timeSpentSeconds for w in worklogs]
        self.timespent += timedelta(seconds=sum(seconds))
        if isinstance(self._parent, Issue):
            self._parent.timespent += self.timespent

    def calc_timespent_by_author(self, worklogs):
        for w in worklogs:
            if self.timespent_by_author.get(w.author.name) is None:
                self.timespent_by_author[w.author.name] = timedelta(seconds=w.timeSpentSeconds)
            else:
                self.timespent_by_author[w.author.name] += timedelta(seconds=w.timeSpentSeconds)
