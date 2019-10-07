import argparse
from datetime import datetime
from entities.jira_client import JiraClient

parser = argparse.ArgumentParser()

parser.add_argument('-l', '--login', default=None, type=str, required=True,
                    help='Логин пользователя Jira')
parser.add_argument('-p', '--password', default=None, required=True,
                    type=str, help="Пароль пользователя Jira")
parser.add_argument('-q', '--query', default=None, type=str, required=True,
                    help='Строка запроса в кавычках "" для получения необходимого списка задач')
parser.add_argument('-f', '--filename', default=str(datetime.now().strftime('%d-%m %H-%M-%S')), type=str,
                    help='Наименование файла с отчетом')
parser.add_argument('-s', '--sheet', default='sheet1', type=str,
                    help='Наименование листа')
parser.add_argument('-sr', '--startrow', default=0, type=int,
                    help='Номер начального столбца')
parser.add_argument('-sc', '--startcol', default=0, type=int,
                    help='Номер начальной колонки')
parser.add_argument('-j', '--jira', default='https://jira.a1qa.com', type=str,
                    help='Адрес сервера Jira для отправки запросов')

args = parser.parse_args()


def main():
    client = None
    try:
        print('Попытка Авторизации в Jira')
        client = JiraClient(host=args.jira,
                            login=args.login,
                            password=args.password)
        client.issues.search_issues(jql=args.query)
        client.issues.collect_worklogs()
        client.worklogs_to_excel(filename=args.filename,
                                 sheet=args.sheet,
                                 jql=args.query,
                                 startrow=args.startrow,
                                 startcol=args.startcol)
        client.close_connection()
    except (KeyboardInterrupt, SystemExit):
        client.close_connection() if client is not None else None
        print('Выход')
        raise
    except Exception as e:
        client.close_connection() if client is not None else None
        print('Ошибка при выполнении')
        raise e


if __name__ == '__main__':
    main()
