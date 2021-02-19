import string
import random
import datetime

import trader.data_base.connection as con

class Base:
    def __init__(self):
        self._db_filepath = None

    # brief: executes one sql-statement
    # param: sql - target sql-statement
    # param: args - arguments for filling the sql-statement
    # return: result of execution of the sql-statement
    def _ExecuteOne(self, sql, *args):
        with con.Connection(self._db_filepath) as connect:
            with connect.GetCursore() as cur:
                return cur.ExecuteOne(sql, *args)

    # brief: executes many sql-statements
    # param: sql - target sql-statement
    # param: args - arguments for filling the sql-statement
    # return: result of execution of the sql-statement
    def _ExecuteMany(self, sql, *args):
        with con.Connection(self._db_filepath) as connect:
            with connect.GetCursore() as cur:
                return cur.ExecuteMany(sql, *args)

    # NOTE: Set...
    
    def SetFilePath(self, filepath):
        self._db_filepath = filepath

    # NOTE: cls. ...

    @classmethod
    def GetDatetime(cls):
        return datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")

    @classmethod
    def CreateId(cls, length=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
