import os
from datetime import datetime
from pathlib import Path

from atlassian import Bitbucket

from entities.excel_tables import PullRequestsTable
from entities.pull_request import PullRequest, PullRequestsByAuthor


class BitbucketClient(Bitbucket):
    DATE_FORMAT = '%d.%m.%y'

    def __init__(self, url, **kwargs):
        super().__init__(url=url, **kwargs)
        self.pull_requests = []
        self.pull_requests_by_author = []

    def collect_pull_requests(self, project, repository='', limit=100, state='All', date_from=None, date_to=None):
        date_from = date_from if not date_from else datetime.strptime(date_from, self.DATE_FORMAT)
        date_to = str(datetime.now().strftime('%d.%m.%y')) if not date_to \
            else datetime.strptime(date_to, self.DATE_FORMAT)

        repositories = self.get_repo_list(project=project, repository=repository)

        for repo_name in repositories:
            self.get_pull_requests_by_repo_name(project=project,
                                                repo_name=repo_name,
                                                state=state,
                                                limit=limit,
                                                date_from=date_from,
                                                date_to=date_to)

        print('Собрана информация по {} Pull Requests'.format(len(self.pull_requests)))

        for pull_request in self.pull_requests:
            self.collect_info_by_pr_author(pull_request=pull_request)

        return self.pull_requests

    def get_repo_list(self, project, repository):
        if not repository or repository == 'all':
            repo_list = self.repo_all_list(project_key=project)
            repositories = [repo['name'] for repo in repo_list]
        else:
            repositories = repository.split(',')

        return repositories

    def get_pull_requests_by_repo_name(self, project, repo_name, state, limit, date_from=None, date_to=None):
        pr_list = self.get_pull_requests(project=project,
                                         repository=repo_name,
                                         state=state,
                                         limit=limit)
        for info in pr_list:
            pull_request = PullRequest(client=self, project=project, repository=repo_name, **info)
            if date_from is None:
                self.pull_requests.append(pull_request)
            else:
                if date_from <= pull_request.cre_date <= date_to:
                    self.pull_requests.append(pull_request)

    def collect_info_by_pr_author(self, pull_request):
        by_author = [elem for elem in self.pull_requests_by_author if all([pull_request.author == elem.author,
                                                                           pull_request.repository == elem.repository])]
        if by_author:
            by_author[0].pr_count += 1
            if pull_request.comments:
                by_author[0].comments.extend(pull_request.comments)
                by_author[0].faults += len(pull_request.comments)
        else:
            by_author_new = PullRequestsByAuthor(author=pull_request.author, repository=pull_request.repository)
            by_author_new.pr_count = 1
            if pull_request.comments:
                by_author_new.comments.extend(pull_request.comments)
                by_author_new.faults = len(pull_request.comments)
            self.pull_requests_by_author.append(by_author_new)

    def pull_requests_to_excel(self, filename, sheet, startrow=0, startcol=0):
        table = PullRequestsTable(bitbucket_client=self)

        for by_author in self.pull_requests_by_author:
            table.insert_data_for_author_into_table(by_author)

        table.to_excel(directory=str(Path(__file__).parent.parent.absolute()) + os.sep + 'reports' + os.sep,
                       filename=filename,
                       startrow=startrow, startcol=startcol, sheet_name=sheet)

    def count_pull_requests_faults(self):
        for prs_by_author in self.pull_requests_by_author:
            prs_by_author.count_faults()

    def close_connection(self):
        self._session.close()
