import pytest

from entities.bitbucket_client import BitbucketClient
from entities.jira_client import JiraClient


TEST_JQL = 'TEST_JQL'


@pytest.fixture(scope='session')
def jira_client():
    client = JiraClient(host='https://jira.a1qa.com', login='login', password='password')
    yield client
    client.close_connection()


@pytest.fixture(scope='session')
def bitbucket_client():
    client = BitbucketClient(url='', username='', password='')
    yield client
    client.close_connection()


@pytest.mark.parametrize('exp_count, jql',
                         [pytest.param(8, TEST_JQL)])
def test_jira_search_issues(jira_client, exp_count, jql):
    issues = jira_client.search_issues(jql=jql)
    assert len(issues) == exp_count


@pytest.mark.parametrize('filename, sheet_name, jql, startrow, startcol',
                         [pytest.param('test_filename', 'test_sheet_name', TEST_JQL, 0, 0)])
def test_jira_worklogs_to_excel(jira_client, filename, sheet_name, jql, startrow, startcol):
    jira_client.search_issues(jql=jql)
    jira_client.issues.collect_worklogs()
    jira_client.worklogs_to_excel(filename=filename, sheet=sheet_name, jql=jql,
                                  startrow=startrow, startcol=startcol)


def test_bitbucket_get_pr(bitbucket_client):
    bitbucket_client.collect_pull_requests(project='', repository='')

