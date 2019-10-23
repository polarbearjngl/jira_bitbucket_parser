from atlassian import Bitbucket

from entities.pull_request import PullRequest, PullRequestsByAuthor


class BitbucketClient(Bitbucket):
    DATE_FORMAT_SHORT = '%d.%m.%y'

    def __init__(self, url, **kwargs):
        super().__init__(url=url, **kwargs)
        self.pull_requests = []
        self.pull_requests_by_author = []

    def collect_pull_requests(self, project, repository, limit=100, state='All'):
        pr_list = self.get_pull_requests(project=project,
                                         repository=repository,
                                         state=state,
                                         limit=limit)
        self.pull_requests.extend([
            PullRequest(client=self, project=project, repository=repository, **info) for info in pr_list
        ])

        for pr in self.pull_requests:
            by_author = [elem for elem in self.pull_requests_by_author if pr.author == elem.author]
            if by_author:
                by_author[0].pr_count += 1
                if pr.comments:
                    by_author[0].comments.extend(pr.comments)
                    by_author[0].faults += len(pr.comments)
            else:
                by_author_new = PullRequestsByAuthor(author=pr.author)
                by_author_new.pr_count = 1
                if pr.comments:
                    by_author_new.comments.extend(pr.comments)
                    by_author_new.faults = len(pr.comments)
                self.pull_requests_by_author.append(by_author_new)

        return self.pull_requests

    def close_connection(self):
        self._session.close()
