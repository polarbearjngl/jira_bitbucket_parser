from entities.jira.worklog_by_author import WorklogByAuthor


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
            self.by_author[w.author.name].update_worklogs_by_issue(seconds=w.timeSpentSeconds, issue=issue,
                                                                   worklog_comments=w.comment)
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
