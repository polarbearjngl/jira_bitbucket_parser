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
