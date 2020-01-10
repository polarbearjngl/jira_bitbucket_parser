import re
from datetime import datetime

from entities.jira.issue import Issue
from entities.jira.worklogs_by_author import WorklogsByAuthor


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

    def collect_worklogs(self, date_from, date_to):
        """Вызов сбора ворклогов для задач, найденных в результате поиска.

        Args:
            date_from: Дата от которой производится поиск ворклогов.
            date_to: Дата до которой производится поиск ворклогов.
        """
        sub_tasks_count, tasks_count = 0, 0
        for issues_list in self.all_issues.values():
            for task in issues_list:
                tasks_count += 1
                for _ in task.subtasks:
                    sub_tasks_count += 1

        print('Начат сбор ворклогов от %s до %s для %s подзадач и %s задач' % (date_from, date_to,
                                                                               sub_tasks_count, tasks_count))

        for issues_list in self.all_issues.values():
            for task in issues_list:
                if task.worklog is not None:
                    # Если ворклогов больше чем возвращается по умолчанию,
                    # то вызываем запрос для получения полных ворклогов
                    if task.worklog_max_results < task.worklog_total:
                        task_worklogs = self.jira.worklogs(issue=task.id)
                    else:
                        task_worklogs = task.worklog.worklogs
                    # брать только ворклоги, которые входят в заданный интервал дат
                    task_worklogs = [t_w for t_w in task_worklogs
                                     if self.check_worklog_date(worklog=t_w, date_from=date_from, date_to=date_to)]
                    task.calc_timespent(worklogs=task_worklogs)
                    task.calc_timespent_by_author(worklogs=task_worklogs)
                    self.worklogs_by_author.update_worklogs_for_author(worklogs=task_worklogs, issue=task)
                    self.worklogs_by_author.update_issues_for_author(issue=task)
                # Для каждой подзадачи вызываем запрос для получения ворклогов
                for subtask in task.subtasks:
                    subtask_worklogs = self.jira.worklogs(issue=subtask.id)
                    # брать только ворклоги, которые входят в заданный интервал дат
                    subtask_worklogs = [st_w for st_w in subtask_worklogs
                                        if self.check_worklog_date(worklog=st_w, date_from=date_from, date_to=date_to)]
                    subtask.calc_timespent(worklogs=subtask_worklogs)
                    task.calc_timespent_by_author(worklogs=subtask_worklogs)
                    self.worklogs_by_author.update_worklogs_for_author(worklogs=subtask_worklogs, issue=subtask)
                    self.worklogs_by_author.update_issues_for_author(issue=subtask)
        print('Закончен сбор ворклогов')

    @staticmethod
    def check_worklog_date(worklog, date_from, date_to):
        """Проверка входит ли дата создания ворклога в заданный интервал дат.

        Args:
            worklog: Данные по ворклогу из API.
            date_from: Дата от которой производится поиск ворклогов.
            date_to: Дата до которой производится поиск ворклогов.

        Returns: True\False.

        """
        worklog_date = datetime.strptime(re.search(r'\d+-\d+-\d+', worklog.created).group(), '%Y-%m-%d')
        return date_from <= worklog_date <= date_to
