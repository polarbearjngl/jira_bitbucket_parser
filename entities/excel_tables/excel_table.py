import os

from pandas import DataFrame, ExcelWriter
from openpyxl import load_workbook


class ExcelTable(dict):
    """Базовый класс для создания объекта эксель-таблицы."""

    # Наименования колонок, которые должны присутствовать в таблице
    COLUMNS = []
    # Наименование директории, в которую должен быть сохранен отчет
    DIR_NAME = ''
    EXTENSION = '.xlsx'

    def get(self, key):
        return getattr(self, key, [])

    def to_excel(self, directory, filename, startrow, startcol, sheet_name):
        """Сохранить собранные данные в эксель-файл."""
        directory = directory + self.DIR_NAME
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = directory + filename + self.EXTENSION

        writer = None
        try:
            book = load_workbook(filename)
            writer = ExcelWriter(filename, engine='openpyxl')
            writer.book = book
        except FileNotFoundError:
            pass

        df = DataFrame(data={k: v for k, v in self.__dict__.items() if k in self.COLUMNS})
        df.to_excel(excel_writer=writer or filename,
                    sheet_name=sheet_name,
                    startrow=startrow, startcol=startcol,
                    index=False)
        if writer:
            writer.save()
            writer.close()
        print('Сохранено в ' + filename + ' на лист ' + sheet_name)
