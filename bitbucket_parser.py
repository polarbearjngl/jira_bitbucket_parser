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
parser.add_argument('-rep', '--repository', default='',
                    type=str, help="Наименование репозитория/репозиториев через запятую")
parser.add_argument('-lim', '--limit', default=100, type=int,
                    help='Максимальное кол-во Pull-requests в ответе')
parser.add_argument('-df', '--date_from', default='', type=str,
                    help='Дата в формате d.m.y от которой производится поиск ПРов')
parser.add_argument('-dt', '--date_to', default='', type=str,
                    help='Дата в формате d.m.y до которой производится поиск ПРов')
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
        client.collect_pull_requests(project=args.project,
                                     repository=args.repository,
                                     limit=args.limit,
                                     date_from=args.date_from,
                                     date_to=args.date_to)
        client.count_pull_requests_faults()
        client.pull_requests_to_excel(filename=args.filename,
                                      sheet=args.sheet,
                                      startrow=args.startrow,
                                      startcol=args.startcol)
    except (KeyboardInterrupt, SystemExit):
        client.close_connection() if client is not None else None
        raise
    except Exception as e:
        client.close_connection() if client is not None else None
        print('Ошибка при выполнении\n')
        print_exc()
        raise e


if __name__ == '__main__':
    main()
