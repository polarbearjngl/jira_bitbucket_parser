import re
from datetime import datetime


class PullRequest(object):

    JIRA_ISSUE_URL_PATTERN = r'(https:|http:|www\.)\S*[jira]\S*'

    def __init__(self, client, project, repository, **kwargs):
        self.client = client,
        self.project = project
        self.repository = repository
        self.id = kwargs.get('id')
        self.title = kwargs.get('title')
        self.description = kwargs.get('description')
        self.author = kwargs.get('author').get('user').get('displayName')
        self.state = kwargs.get('state')
        self.cre_date = datetime.fromtimestamp(kwargs.get('createdDate') / 1000)
        self.activities = []
        self.comments = []
        self.get_activities_and_comments()
        self.tests_count_in_pr = self.get_tests_count()

    def get_activities_and_comments(self):
        self.activities = self.client[0].get_pull_requests_activities(project=self.project,
                                                                      repository=self.repository,
                                                                      pull_request_id=self.id)
        self.comments.extend([text['comment']['text'] for text in
                              [act for act in self.activities if act['action'] == 'COMMENTED']])

    def get_tests_count(self):
        founded_url = re.findall(self.JIRA_ISSUE_URL_PATTERN, self.description) if self.description else None
        if founded_url:
            return len(founded_url)

        return 0


class PullRequestsByAuthor(object):

    COMMON_PATTERN = r'^\[(..)]'
    HIGH_PATTERN = r'^h.'
    MEDIUM_PATTERN = r'^m.'
    LOW_PATTERN = r'^l.'

    def __init__(self, author, repository, tests_count):
        self.author = author
        self.repository = repository
        self.tests_count = tests_count
        self.pr_count = 0
        self.faults = 0
        self.high = 0
        self.medium = 0
        self.low = 0
        self.no_category = 0
        self.by_severity = {}
        self.founded_severities = []
        self.comments = []

    def count_faults(self):
        for comment in self.comments:
            string = re.findall(self.COMMON_PATTERN, comment)
            if not string:
                self.no_category += 1
            else:
                self.founded_severities.extend(string)

        self.get_faults_severity()

    def get_faults_severity(self):
        for string in self.founded_severities:
            for pattern in [self.HIGH_PATTERN, self.MEDIUM_PATTERN, self.LOW_PATTERN]:
                severity = re.findall(pattern, string)
                if severity and pattern == self.HIGH_PATTERN:
                    self.high += 1
                if severity and pattern == self.MEDIUM_PATTERN:
                    self.medium += 1
                if severity and pattern == self.LOW_PATTERN:
                    self.low += 1
                if severity:
                    faults_severity = self.by_severity.get(severity[0])
                    if faults_severity:
                        self.by_severity[severity[0]] += 1
                    else:
                        self.by_severity.update({severity[0]: 1})
                    break
