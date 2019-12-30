from datetime import datetime

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
def bitbucket_client(jira_client):
    client = BitbucketClient(url='', username='', password='',
                             jira_client=jira_client)
    yield client
    client.close_connection()


@pytest.mark.parametrize('exp_count, jql',
                         [pytest.param(8, TEST_JQL)])
def test_jira_search_issues(jira_client, exp_count, jql):
    issues = jira_client.search_issues(jql=jql)
    assert len(issues) == exp_count


@pytest.mark.parametrize('filename, jql, startrow, startcol',
                         [pytest.param(str(datetime.now().strftime('%d-%m %H-%M-%S')), TEST_JQL, 0, 0)])
def test_jira_worklogs_to_excel(jira_client, filename, jql, startrow, startcol):
    jira_client.search_issues(jql=jql)
    jira_client.issues.collect_worklogs()
    jira_client.worklogs_to_excel(filename=filename, jql=jql,
                                  startrow=startrow, startcol=startcol)


@pytest.mark.parametrize('filename, sheet_name, startrow, startcol',
                         [pytest.param(str(datetime.now().strftime('%d-%m %H-%M-%S')), 'test_sheet_name', 0, 0)])
def test_bitbucket_get_pr(bitbucket_client, filename, sheet_name, startrow, startcol):
    bitbucket_client.collect_pull_requests(project='', repository='',
                                           date_from='01.10.19', date_to='31.10.19')
    bitbucket_client.count_pull_requests_faults()
    bitbucket_client.pull_requests_to_excel(filename=filename, sheet=sheet_name, startrow=startrow, startcol=startcol)
