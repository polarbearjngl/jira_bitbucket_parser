import argparse
from datetime import datetime
from entities.jira_client import JiraClient
from traceback import print_exc

parser = argparse.ArgumentParser()

parser.add_argument('-l', '--login', default=None, type=str, required=True,
                    help='Логин пользователя Jira')
parser.add_argument('-p', '--password', default=None, required=True,
                    type=str, help="Пароль пользователя Jira")
parser.add_argument('-q', '--query', default=None, type=str, required=True,
                    help='Строка запроса в кавычках "" для получения необходимого списка задач')
parser.add_argument('-f', '--filename', default=str(datetime.now().strftime('%d-%m %H-%M-%S')), type=str,
                    help='Наименование файла с отчетом')
parser.add_argument('-df', '--date_from', default=None, type=str,
                    help='Дата в формате d.m.y от которой производится поиск ворклогов')
parser.add_argument('-dt', '--date_to', default=None, type=str,
                    help='Дата в формате d.m.y до которой производится поиск ворклогов')
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
        client.search_issues(jql=args.query)
        date_to = datetime.strptime(args.date_to, '%d.%m.%y') if args.date_to is not None else datetime.now()
        date_from = datetime.strptime(args.date_from, '%d.%m.%y') \
            if args.date_from is not None else datetime.strptime('01-01-16', '%d-%m-%y')
        client.issues.collect_worklogs(date_from=date_from, date_to=date_to)
        client.worklogs_to_excel(filename=args.filename,
                                 jql=args.query,
                                 startrow=args.startrow,
                                 startcol=args.startcol)
        client.close_connection()
        input("\nНажмите Enter для выхода...")
    except (KeyboardInterrupt, SystemExit):
        client.close_connection() if client is not None else None
        raise
    except Exception as e:
        client.close_connection() if client is not None else None
        print('Ошибка при выполнении\n')
        print_exc()
        input("\nНажмите Enter для выхода...")
        raise e


if __name__ == '__main__':
    main()
