class PullRequest(object):

    def __init__(self, client, project, repository, **kwargs):
        self.client = client,
        self.project = project
        self.repository = repository
        self.id = kwargs.get('id')
        self.author = kwargs.get('author').get('user').get('displayName')
        self.state = kwargs.get('state')
        self.activities = []
        self.comments = []
        self.get_activities_and_comments()

    def get_activities_and_comments(self):
        self.activities = self.client[0].get_pull_requests_activities(project=self.project,
                                                                      repository=self.repository,
                                                                      pull_request_id=self.id)
        self.comments.extend([text['comment']['text'] for text in
                              [act for act in self.activities if act['action'] == 'COMMENTED']])


class PullRequestsByAuthor(object):

    def __init__(self, author):
        self.author = author
        self.pr_count = 0
        self.faults = 0
        self.faults_severity = {'high': 0, 'medium': 0, 'low': 0, 'no info': 0}
        self.comments = []
