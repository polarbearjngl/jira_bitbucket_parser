import os

from entities.excel_tables.excel_table import ExcelTable


class PullRequestsTable(ExcelTable):
    COLUMNS = ['repository',
               'component',
               'author',
               'pull requests',
               'tests count',
               'faults',
               'high',
               'medium',
               'low',
               'no category',
               'high readability',
               'high structural',
               'high logical',
               'high code complexity',
               'high code issue',
               'medium readability',
               'medium structural',
               'medium logical',
               'medium code complexity',
               'medium code issue',
               'low readability',
               'low structural',
               'low logical',
               'low code complexity',
               'low code issue']

    DIR_NAME = 'pull_requests' + os.sep

    def __init__(self, bitbucket_client, **kwargs):
        super().__init__(**kwargs)
        self.bitbucket_client = bitbucket_client
        for key in self.COLUMNS:
            setattr(self, key, [])

    def insert_data_for_author_into_table(self, by_author):
        self.get('repository').append(by_author.repository)
        self.get('component').append(by_author.component)
        self.get('author').append(by_author.author)
        self.get('pull requests').append(by_author.pr_count)
        self.get('tests count').append(by_author.tests_count)
        self.get('faults').append(by_author.faults)
        self.get('high').append(by_author.high)
        self.get('medium').append(by_author.medium)
        self.get('low').append(by_author.low)
        self.get('no category').append(by_author.no_category)
        self.get('high readability').append(by_author.hr)
        self.get('high structural').append(by_author.hs)
        self.get('high logical').append(by_author.hl)
        self.get('high code complexity').append(by_author.hx)
        self.get('high code issue').append(by_author.hc)
        self.get('medium readability').append(by_author.mr)
        self.get('medium structural').append(by_author.ms)
        self.get('medium logical').append(by_author.ml)
        self.get('medium code complexity').append(by_author.mx)
        self.get('medium code issue').append(by_author.mc)
        self.get('low readability').append(by_author.lr)
        self.get('low structural').append(by_author.ls)
        self.get('low logical').append(by_author.ll)
        self.get('low code complexity').append(by_author.lx)
        self.get('low code issue').append(by_author.lc)
