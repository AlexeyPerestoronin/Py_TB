import sqlite3

import trader.db.__cursore as cur

# brief: class implements up covering capsule for sqlite3.connection-class
class Connection:
    def __init__(self, db_filepath):
        self._db_filepath = db_filepath
        self._connection = None

    def __enter__(self):
        self._connection = sqlite3.connect(self._db_filepath)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()

    def GetCursore(self):
        return cur.Cursor(self._connection)
