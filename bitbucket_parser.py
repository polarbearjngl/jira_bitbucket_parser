import argparse
from datetime import datetime
from entities.bitbucket_client import BitbucketClient
from traceback import print_exc

parser = argparse.ArgumentParser()

parser.add_argument('-l', '--login', default=None, type=str, required=True,
                    help='Логин пользователя Bitbucket')
parser.add_argument('-p', '--password', default=None, required=True,
                    type=str, help="Пароль пользователя Bitbucket")
parser.add_argument('-prj', '--project', default=None, required=True,
                    type=str, help="Наименование проекта Bitbucket")
parser.add_argument('-rep', '--repository', default=None, required=True,
                    type=str, help="Наименование репозитория Bitbucket")
parser.add_argument('-l', '--limit', default=100, type=int,
                    help='Максимальное кол-во Pull-requests в ответе')
parser.add_argument('-f', '--filename', default=str(datetime.now().strftime('%d-%m %H-%M-%S')), type=str,
                    help='Наименование файла с отчетом')
parser.add_argument('-s', '--sheet', default='sheet1', type=str,
                    help='Наименование листа')
parser.add_argument('-sr', '--startrow', default=0, type=int,
                    help='Номер начального столбца')
parser.add_argument('-sc', '--startcol', default=0, type=int,
                    help='Номер начальной колонки')
parser.add_argument('-b', '--bitbucket', type=str, required=True,
                    help='Адрес сервера Bitbucket для отправки запросов')

args = parser.parse_args()


def main():
    client = None
    try:
        print('Попытка Авторизации в Bitbucket')
        client = BitbucketClient(url=args.bitbucket,
                                 username=args.login,
                                 password=args.password)
        pull_requests = client.collect_pull_requests(project=args.project,
                                                     repository=args.repository,
                                                     state='All',
                                                     limit=args.limit)
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
