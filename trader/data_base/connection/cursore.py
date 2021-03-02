import copy
import decimal

# brief: class implements up covering capsule for sqlite3.connection.cursor-class
class Cursor:
    def __init__(self, connection):
        self._connection = connection
        self._cursore = None

    def __enter__(self):
        self._cursore = self._connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.commit()
        self._cursore.close()

    def ExecuteOne(self, sql, *args):
        target_args = []
        for arg in args:
            if isinstance(arg, decimal.Decimal):
                target_args.append(float(arg))
            else:
                target_args.append(copy.deepcopy(arg))
        self._cursore.execute(sql, target_args)
        return self._cursore.fetchall()

    def ExecuteMany(self, sql, *args):
        self._cursore.executemany(sql, args)
        return self._cursore.fetchall()
