from datetime import timedelta


class Issues(object):
    """Класс для работы со списком задач."""

    def __init__(self, connection):
        self.jira = connection
        self.all_issues = {}

    def search_issues(self, jql, fields='issue,key,summary,subtasks,worklog,assignee,status,type'):
        """Поиск задач в джира, подходящих под заданный jql запрос.

        Args:
            jql: Текст запроса.
            fields: Строка с перечислением полей, которые вернутся в ответе.

        Returns:
            Список вернувшихся задач.

        """
        issues_list = self.jira.search_issues(jql_str=jql,
                                              maxResults=False,
                                              fields=fields,
                                              expand='worklog')
        self.all_issues[jql] = [Issue(jira_issue=issue, parent=self) for issue in issues_list]
        print('По данному запросу найдено %s задач' % len(self.all_issues[jql]))
        return self.all_issues[jql]

    def collect_worklogs(self):
        """Вызов сбора ворклогов для задач, найденных в результате поиска."""
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
                    # Если ворклогов больше чем возвращается по умолчанию,
                    # то вызываем запрос для получения полных ворклогов
                    if task.worklog_max_results < task.worklog_total:
                        task_worklogs = self.jira.worklogs(issue=task.id)
                    else:
                        task_worklogs = task.worklog.worklogs
                    task.calc_timespent(worklogs=task_worklogs)
                    task.calc_timespent_by_author(worklogs=task_worklogs)
                # Для каждой подзадачи вызываем запрос для получения ворклогов
                for subtask in task.subtasks:
                    subtask_worklogs = self.jira.worklogs(issue=subtask.id)
                    subtask.calc_timespent(worklogs=subtask_worklogs)
                    task.calc_timespent_by_author(worklogs=subtask_worklogs)
        print('Закончен сбор ворклогов')


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
        self.summary = jira_issue.fields.summary
        self.type = jira_issue.fields.issuetype
        self.assignee = getattr(jira_issue.fields, 'assignee', '')
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
