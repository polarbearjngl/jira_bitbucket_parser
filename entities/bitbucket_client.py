import os
from datetime import datetime
from pathlib import Path

from atlassian import Bitbucket

from entities.bitbucket.pull_request import PullRequest
from entities.bitbucket.pull_requests_by_author import PullRequestsByAuthor
from entities.excel_tables.pull_requests_table import PullRequestsTable


class BitbucketClient(Bitbucket):
    """Клиент для работы с API Bitbucket."""
    DATE_FORMAT = '%d.%m.%y'

    def __init__(self, url, jira_client=None, **kwargs):
        """

        Args:
            url: URL Bitbucket.

        Kwargs:
            username: Пользователь.
            password: Пароль.

        """
        super().__init__(url=url, **kwargs)
        self.jira_client = jira_client.jira if jira_client else None
        self.pull_requests = []
        self.pull_requests_by_author = []

    def collect_pull_requests(self, project, repository='', limit=100, state='All', date_from=None, date_to=None):
        """Сбор пулл реквестов. Обработка статистики по пулл реквестам.

        Args:
            project: Наименование проекта в Bitbucket.
            repository: Наименование репозитория/репозиториев через запятую. Если all, то будет собрана
                        статистика по всем репозиториям в проекте.
            limit: Количество результатов на одной странице ответа.
            state: Статус ПРа. Если All, то будут собраны все ПРы.
            date_from: Дата в формате d.m.y от которой производится поиск ПРов.
            date_to: Дата в формате d.m.y до которой производится поиск ПРов.

        """
        date_from = date_from if not date_from else datetime.strptime(date_from, self.DATE_FORMAT)
        date_to = str(datetime.now().strftime('%d.%m.%y')) if not date_to \
            else datetime.strptime(date_to, self.DATE_FORMAT)

        repositories = self.get_repo_list(project=project, repository=repository)

        print('Сбор информации по ПРам. Выбрано репозиториев: {}'.format(len(repositories)))

        for repo_name in repositories:
            self.get_pull_requests_by_repo_name(project=project,
                                                repo_name=repo_name,
                                                state=state,
                                                limit=limit,
                                                date_from=date_from,
                                                date_to=date_to)

        print('Собрана информация по {} ПРам'.format(len(self.pull_requests)))

        for pull_request in self.pull_requests:
            self.collect_info_by_pr_author(pull_request=pull_request)

        return self.pull_requests

    def get_repo_list(self, project, repository):
        """Определение наименования репозиториев, для которых будет производится поиск.

        Args:
            project: Наименование проекта.
            repository: Наименование репозитория/репозиториев через запятую. Если all, то будет собрана
                        статистика по всем репозиториям в проекте.

        Returns: Наименования репозиториев.

        """
        if not repository or repository == 'all':
            repo_list = self.repo_all_list(project_key=project)
            repositories = [repo['name'] for repo in repo_list]
        else:
            repositories = repository.split(',')

        return repositories

    def get_pull_requests_by_repo_name(self, project, repo_name, state, limit, date_from=None, date_to=None):
        """Получение ПРов для конкретного репозитория.

        Args:
            project: Наименование проекта в Bitbucket.
            repo_name: Наименование репозитория.
            state: Статус ПРа. Если All, то будут собраны все ПРы.
            limit: Количество результатов на одной странице ответа.
            date_from: Дата в формате d.m.y от которой производится поиск ПРов.
            date_to: Дата в формате d.m.y до которой производится поиск ПРов.

        """
        pr_list = self.get_pull_requests(project=project,
                                         repository=repo_name,
                                         state=state,
                                         limit=limit)

        # не собираем статистику по отклоненным ПРам
        for info in [pr for pr in pr_list if pr['state'] != 'DECLINED']:
            pull_request = PullRequest(client=self, jira_client=self.jira_client, project=project, repository=repo_name, **info)
            if not date_from:
                self.pull_requests.append(pull_request)
            elif any([date_from <= pull_request.cre_date <= date_to,
                      pull_request.cre_date <= date_to and not date_from]):
                self.pull_requests.append(pull_request)

    def collect_info_by_pr_author(self, pull_request):
        """Сбор статистики по автору ПРа.

        Args:
            pull_request: Объект PullRequest.

        """
        by_author = [elem for elem in self.pull_requests_by_author if all([pull_request.author == elem.author,
                                                                           pull_request.repository == elem.repository,
                                                                           pull_request.component == elem.component])]
        if by_author:
            by_author[0].pr_count += 1
            by_author[0].tests_count += pull_request.tests_count_in_pr
            if pull_request.comments:
                by_author[0].comments.extend(pull_request.comments)
                by_author[0].faults += len(pull_request.comments)
        else:
            by_author_new = PullRequestsByAuthor(author=pull_request.author,
                                                 repository=pull_request.repository,
                                                 tests_count=pull_request.tests_count_in_pr,
                                                 component=pull_request.component)
            by_author_new.pr_count = 1
            if pull_request.comments:
                by_author_new.comments.extend(pull_request.comments)
                by_author_new.faults = len(pull_request.comments)
            self.pull_requests_by_author.append(by_author_new)

    def pull_requests_to_excel(self, filename, sheet, startrow=0, startcol=0):
        """Запись информации о ПРах в excel.

        Args:
            filename: Наименование файла.
            sheet:
            startrow: Номер строки для начала записи.
            startcol: Номер колонки для начала записи.

        """
        table = PullRequestsTable(bitbucket_client=self)

        for by_author in self.pull_requests_by_author:
            table.insert_data_for_author_into_table(by_author)

        table.to_excel(directory=str(Path(__file__).parent.parent.absolute()) + os.sep + 'reports' + os.sep,
                       filename=filename,
                       startrow=startrow, startcol=startcol, sheet_name=sheet)

    def count_pull_requests_faults(self):
        """Подсчет замечаний в собранных ПРах."""
        for prs_by_author in self.pull_requests_by_author:
            prs_by_author.count_faults()

    def close_connection(self):
        self._session.close()
