import os
import sqlite3

from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Database:
    def __init__(self, path: Optional[str] = None):
        self.file_path = path if path else os.environ.get('DATABASE_PATH')

        return

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
            self.cursor.row_factory = self.dict_factory #@todo sqlite3.Row tells the connection to return rows that behave like dicts.
            return None
        except sqlite3.Error as e:
            print(e)

    def disconnect(self):
        self.connection.close()
