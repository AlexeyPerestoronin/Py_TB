import common

import trader.data_base.tables as table
import trader.data_base.tables.consts as table_const
import trader.data_base.tables.errors as table_error

class Trader(table.Base):
    _sql = {
        "create_table" :
"""
-- brief: table for presenting one exchange-trader
CREATE TABLE IF NOT EXISTS "Trader"
(
id              TEXT    NOT NULL,                    -- trader identificator
status          TEXT    NOT NULL DEFAULT "void",     -- current trade-status
params          TEXT    NOT NULL,                    -- trader parameters
profit          FLOAT   NULL DEFAULT 0.0,            -- finalize profit from trading
time_start      TEXT    NULL,                        -- time of strart trading
time_stop       TEXT    NULL,                        -- time of stop trading
PRIMARY KEY("id"),
CHECK(status in ("void", "during", "finished"))
);
""",
        "find"              : 'SELECT id FROM "Trader" WHERE params=?1 AND status!="finished";',
        "create_trader"     : 'INSERT INTO "Trader" (id, params, time_start) VALUES (?1, ?2, ?3);',
        "get_status"        : 'SELECT status FROM "Trader" WHERE id=?1;',
        "get_profit"        : 'SELECT profit FROM "Trader" WHERE id=?1;',
        "get_quantity"      : 'SELECT COUNT(*) FROM "Trader" WHERE id=?1;',
        "increase_profit"   : 'UPDATE "Trader" SET profit=(?1+(SELECT profit FROM "Trader" WHERE id=?2)) WHERE id=?2;',
        "set_stoptime"      : 'UPDATE "Trader" SET time_stop=?1 WHERE id=?2;',
        "set_status"        : 'UPDATE "Trader" SET status=?1 WHERE id=?2;',
    }

    def __init__(self):
        table.Base.__init__(self)
        self._id = None
        self._params = None

    def _SetTraderStopTime(self):
        self._ExecuteOne(self._sql["set_stoptime"], self.GetDatetime(), self._id)

    def _SetTraderStatus(self, status):
        self._ExecuteOne(self._sql["set_status"], status, self._id)

    def Is(self):
        if not self._id:
            return False
        return True

    def Check(self):
        if not self._id:
            raise table_error.TraderIsNotCreate()

    # NOTE: Set...

    def SetParams(self, params):
        self._params = params

    # NOTE: SetAs...

    def SetAsDuring(self):
        self.Check()
        self._SetTraderStatus(table_const.Status.Trader.DURING)

    def SetAsFinished(self):
        self.Check()
        self._SetTraderStatus(table_const.Status.Trader.FINISHED)

    # NOTE: Get...

    def GetId(self):
        self.Check()
        return self._id

    def GetPtofit(self):
        self.Check()
        return float(self._ExecuteOne(self._sql["get_profit"], self._id)[0][0])

    def GetStatus(self):
        self.Check()
        return self._ExecuteOne(self._sql["get_status"], self._id)[0][0]

    # NOTE: ...

    def IncreaseProfit(self, profit):
        self.Check()
        self._ExecuteOne(self._sql["increase_profit"], profit, self._id)

    def Init(self):
        self._ExecuteOne(self._sql["create_table"])

    def Find(self):
        self._id = common.TryExecute(lambda : self._ExecuteOne(self._sql["find"], self._params)[0][0])
        if not self._id:
            raise table_error.NotAvailableTraderByParams()

    def Create(self, id=None):
        if not id:
            id = self.CreateId()
        self._id = id
        self._ExecuteOne(self._sql["create_trader"], self._id, self._params, self.GetDatetime())

    def Finish(self):
        self.Check()
        self._SetTraderStopTime()
        self.SetAsFinished()
        result_profit = self.GetPtofit()
        self._id = None
        return result_profit
