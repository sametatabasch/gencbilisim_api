import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        return

    file_path = os.environ.get('DATABASE_PATH')
    connection = None
    cursor = None

    def dict_factory(self, cursor, row):
        """
            change factory for novel syntax of json api
            database data return dict instead of tuple
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.file_path)
            self.cursor = self.connection.cursor()
            self.cursor.row_factory = self.dict_factory
            return None
        except sqlite3.Error as e:
            print(e)

    def disconnect(self):
        self.connection.close()
