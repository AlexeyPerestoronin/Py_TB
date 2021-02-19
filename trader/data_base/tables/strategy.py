import common

import strategy.const.errors as strategy_error

import trader.data_base.tables as table
import trader.data_base.tables.consts as table_const
import trader.data_base.tables.errors as table_error

class Strategy(table.Base):
    _sql = {
        "create_table" :
"""
-- brief: table for presenting one trade-strategy
CREATE TABLE IF NOT EXISTS "Strategy"
(
id              TEXT    NOT NULL,                    -- trade-strategy identificator
id_t            TEXT    NOT NULL,                    -- identificator of master-trader
status          TEXT    NOT NULL DEFAULT "void",     -- current trade-strategy-status
recovery        TEXT    NULL,                        -- trade-strategy recovery-string
preview         TEXT    NULL,                        -- trade-strategy preview-string
profit          FLOAT   NULL DEFAULT 0.0,            -- finalize profit from trade-strategy
time_start      TEXT    NULL,                        -- time of initializing strategy
time_stop       TEXT    NULL,                        -- time of closing strategy
PRIMARY KEY("id"),
FOREIGN KEY(id_t) REFERENCES Trader(id)
CHECK(status in ("void", "init", "trade", "wait", "complete"))
);
""",
        "find"                  : 'SELECT id FROM "Strategy" WHERE id_t=?1 AND status NOT IN ("complete");',
        "create_new"            : 'INSERT INTO "Strategy" (id, id_t, time_start) VALUES (?1, ?2, ?3);',
        "get_status"            : 'UPDATE "Strategy" SET status=?1 WHERE id=?2;',
        "set_stoptime"          : 'UPDATE "Strategy" SET time_stop=?1 WHERE id=?2;',
        "set_recovery_string"   : 'UPDATE "Strategy" SET recovery=?1 WHERE id=?2;',
        "set_preview_string"    : 'UPDATE "Strategy" SET preview=?1 WHERE id=?2;',
        "set_profit"            : 'UPDATE "Strategy" SET profit=?1 WHERE id=?2;',
        "set_status"            :  'SELECT status FROM "Strategy" WHERE id=?1;',
        "get_recovery_string"   : 'SELECT recovery FROM "Strategy" WHERE id=?1;',
        "get_preview_string"    : 'SELECT preview FROM "Strategy" WHERE id=?1;',
        "get_profit"            : 'SELECT profit FROM "Strategy" WHERE id=?1;'
    }

    def __init__(self):
        # data-base(s)
        table.Base.__init__(self)
        self._id = None
        self._trader_id = None
        # callback(s)
        self._GetStrategyRecoverystring = None
        self._GetStrategyPreview = None
        self._GetStrategyProfit = None

    def _SetStrategyStoptime(self):
        self._ExecuteOne(self._sql["set_stoptime"], self.GetDatetime(), self._id)

    def _SetStrategyStatus(self, status):
        self._ExecuteOne(self._sql["get_status"], status, self._id)

    def _SetStrategyProfit(self):
        if self._GetStrategyProfit and self.GetStatus() not in (table_const.Status.Strategy.VOID, table_const.Status.Strategy.INIT):
            strategy_profit = None
            try:
                strategy_profit = self._GetStrategyProfit()
            except strategy_error.SomeErrorInTradeStrategy:
                return
            self._ExecuteOne(self._sql["set_profit"], strategy_profit, self._id)

    def _UpdateStrategyPreview(self):
        if self._GetStrategyPreview:
            strategy_preview = None
            try:
                strategy_preview = self._GetStrategyPreview()
            except strategy_error.SomeErrorInTradeStrategy:
                return
            self._ExecuteOne(self._sql["set_preview_string"], strategy_preview, self._id)

    def _UpdateStrategyRecoverystring(self):
        if self._GetStrategyRecoverystring:
            strategy_recovery = None
            try:
                strategy_recovery = self._GetStrategyRecoverystring()
            except strategy_error.SomeErrorInTradeStrategy:
                return
            self._ExecuteOne(self._sql["set_recovery_string"], strategy_recovery, self._id)

    def Is(self):
        if not self._id:
            return False
        return True

    def Check(self):
        if not self._id:
            raise table_error.StrategyIsNotCreate()

    # NOTE: Set...

    def SetTraderId(self, trader_id):
        self._trader_id = trader_id

    # NOTE: SetAs...

    def SetAsInit(self):
        self.Check()
        self._SetStrategyStatus(table_const.Status.Strategy.INIT)

    def SetAsTrade(self):
        self.Check()
        self._SetStrategyStatus(table_const.Status.Strategy.TRADE)

    def SetAsComplete(self):
        self.Check()
        self._SetStrategyStatus(table_const.Status.Strategy.COMPLETE)

    def SetAsWait(self):
        self.Check()
        self._SetStrategyStatus(table_const.Status.Strategy.WAIT)

    # NOTE: SetCallback...

    def SetCallbackGetStrategyRecoverystring(self, call_object):
        self._GetStrategyRecoverystring = call_object

    def SetCallbackGetStrategyPreview(self, call_object):
        self._GetStrategyPreview = call_object

    def SetCallbackGetStrategyProfit(self, call_object):
        self._GetStrategyProfit = call_object

    # NOTE: Get...

    def GetId(self):
        self.Check()
        return self._id

    def GetRecovery(self):
        self.Check()
        return self._ExecuteOne(self._sql["get_recovery_string"], self._id)[0][0]

    def GetPreview(self):
        self.Check()
        return self._ExecuteOne(self._sql["get_preview_string"], self._id)[0][0]

    def GetProfit(self):
        self.Check()
        return float(self._ExecuteOne(self._sql["get_profit"], self._id)[0][0])

    def GetStatus(self):
        self.Check()
        return self._ExecuteOne(self._sql["set_status"], self._id)[0][0]

    # NOTE: ...

    def Init(self):
        self._ExecuteOne(self._sql["create_table"])

    def Update(self):
        self.Check()
        self._UpdateStrategyRecoverystring()
        self._UpdateStrategyPreview()

    def Find(self):
        self._id = common.TryExecute(lambda : self._ExecuteOne(self._sql["find"], self._trader_id)[0][0])
        if not self._id:
            raise table_error.NotAvailableStrategyForTrader()
        self.Update()

    def Create(self, id=None):
        if not id:
            id = self.CreateId()
        self._id = id
        self._ExecuteOne(self._sql["create_new"], self._id, self._trader_id, self.GetDatetime())
        self.Update()

    def Finish(self):
        self.Check()
        self.Update()
        self._SetStrategyProfit()
        result_profit = self.GetProfit()
        self._SetStrategyStoptime()
        self.SetAsComplete()
        self._id = None
        return result_profit
