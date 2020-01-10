import re


class PullRequestsByAuthor(object):
    """Объект для работы с информацией о ПРе для отдельного Автора."""

    COMMON_PATTERN = r'^\[(..)]'
    HIGH_PATTERN = r'^h.'
    MEDIUM_PATTERN = r'^m.'
    LOW_PATTERN = r'^l.'

    def __init__(self, author, repository, component, tests_count):
        """Создание объекта для работы с информацией о ПРе для отдельного Автора.

        Args:
            author: Автор ПРа.
            repository: Наименование репозитория.
            tests_count: Кол-во тестов
        """
        self.author = author
        self.repository = repository
        self.component = component
        self.tests_count = tests_count
        self.pr_count = 0
        self.faults = 0
        self.high = 0
        self.medium = 0
        self.low = 0
        self.hr = self.hs = self.hl = self.hx = self.hc = self.mr = self.ms = self.ml = 0
        self.mx = self.mc = self.lr = self.ls = self.ll = self.lx = self.lc = self.no_category = 0
        self.founded_severities = []
        self.comments = []

    def count_faults(self):
        """Подсчет ошибок. Сбор инфы по категориям ошибки."""
        for comment in self.comments:
            string = re.findall(self.COMMON_PATTERN, comment)
            if not string:
                self.no_category += 1
            else:
                self.founded_severities.extend(string)

        self.get_faults_severity()

    def get_faults_severity(self):
        """Сбор инфы по категориям ошибки."""
        for string in self.founded_severities:
            for pattern in [self.HIGH_PATTERN, self.MEDIUM_PATTERN, self.LOW_PATTERN]:
                severity = re.findall(pattern, string)
                if severity and pattern == self.HIGH_PATTERN:
                    self.high += 1
                if severity and pattern == self.MEDIUM_PATTERN:
                    self.medium += 1
                if severity and pattern == self.LOW_PATTERN:
                    self.low += 1
                for item in severity:
                    setattr(self, item, getattr(self, item) + 1)
