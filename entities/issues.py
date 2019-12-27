from datetime import timedelta


class Issues(object):
    """Класс для работы со списком задач."""

    def __init__(self, connection):
        self.jira = connection
        self.all_issues = {}
        self.worklogs_by_author = WorklogsByAuthor(parent=self)

    def search_issues(self, jql, fields='issue,key,summary,subtasks,worklog,assignee,status,type,component'):
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
                    self.worklogs_by_author.update_worklogs_for_author(worklogs=task_worklogs, issue=task)
                    self.worklogs_by_author.update_issues_for_author(issue=task)
                # Для каждой подзадачи вызываем запрос для получения ворклогов
                for subtask in task.subtasks:
                    subtask_worklogs = self.jira.worklogs(issue=subtask.id)
                    subtask.calc_timespent(worklogs=subtask_worklogs)
                    task.calc_timespent_by_author(worklogs=subtask_worklogs)
                    self.worklogs_by_author.update_worklogs_for_author(worklogs=subtask_worklogs, issue=subtask)
                    self.worklogs_by_author.update_issues_for_author(issue=subtask)
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


class WorklogsByAuthor(object):
    """Класс для работы со списком ворклогов по всем авторам."""

    def __init__(self, parent):
        self.parent = parent
        self.by_author = {}

    def update_worklogs_for_author(self, worklogs, issue):
        """Обработать ворклог и записать информацию по автору в соответствующую строку таблицы.

        Args:
            worklogs: Информация по ворклогам из задачи или подзадачи.

        """
        for w in worklogs:
            if self.by_author.get(w.author.name) is None:
                self.by_author[w.author.name] = WorklogByAuthor(author=w.author.name)

            self.by_author[w.author.name].update_timespent(w.timeSpentSeconds)
            self.by_author[w.author.name].update_worklogs_by_issue(seconds=w.timeSpentSeconds, issue=issue)
            if w.issueId not in self.by_author[w.author.name].issue_ids:
                self.by_author[w.author.name].issue_ids.append(w.issueId)

    def update_issues_for_author(self, issue):
        """Обработать задачу и добавить информацию о ней в соответсвующую строку таблицы для автора ворклога,
           если он раотал над ней.

        Args:
            issue: Информация о задаче.

        """
        for by_author in self.by_author.values():
            if issue.id in by_author.issue_ids and issue.issue_id not in by_author.issues:
                by_author.summaries = by_author.summaries + issue.summary + '\n'
                by_author.issues = by_author.issues + issue.issue_id + '\n'
                if issue.components and issue.components not in by_author.components:
                    by_author.components = by_author.components + issue.components + '\n'


class WorklogBy(object):

    def __init__(self):
        self.timespent_sec = 0
        self.timespent_min = None
        self.timespent_hours = None

    def update_timespent(self, seconds):
        """Обновить информацию о времени, которое залогано автором.

        Args:
            seconds: Количество секунд, которое будет добавлено.
        """
        self.timespent_sec += seconds
        self.timespent_hours = self.sec_to_hours_mins(s=self.timespent_sec)
        self.timespent_min = self.sec_to_mins(s=self.timespent_sec)

    @staticmethod
    def sec_to_hours_mins(s):
        hours = int(s // 3600)
        mins = (s % 3600) // 60
        if mins == 0:
            return hours
        else:
            mins = str(mins / 60)[2:]
            return float("{}.{}".format(hours, mins))

    @staticmethod
    def sec_to_mins(s):
        return int(str(s // 60))


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


class WorklogByIssueForAuthor(WorklogBy):

    def __init__(self, issue, author):
        super().__init__()
        self.author = author
        self.issue_id = issue.issue_id
        self.summary = issue.summary
        self.type = issue.type
        self.components = issue.components
        self.assignee = issue.assignee
