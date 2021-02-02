import string
import random
import sqlite3
import datetime

import common

import strategy.const as s_const

import trader.const as const
import trader.const.errors as errors
import trader.db.__connection as con

# brief: implements logic of DB controlling for trader
class Simple:
    def __init__(self):
        # data-base(s)
        self._db_filepath = None
        # current trading(s)
        self._trader_id = None
        self._strategy_id = None
        self._order_id_I = None
        self._order_id_S = None
        self._order_id_B = None
        # callback(s)
        self._GetStrategyRecoverystring = None
        self._GetStrategyPreview = None
        self._GetStrategyProfit = None
        self._GetOrderTrueview = None

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

    # brief: creates DB for trader before do business
    def _CreatesDB(self):
        self._ExecuteOne(self._sql_create_table_Trader)
        self._ExecuteOne(self._sql_create_table_Strategy)
        self._ExecuteOne(self._sql_create_table_Order)

    # NOTE: Trader

    def _IsTraderExistByID(self, trader_id):
        is_exist = self._ExecuteOne(self._sql_get_trader_quantity_by_id, trader_id)[0][0]
        return bool(is_exist)

    def _FindTrader(self, params):
        self._trader_id = common.TryExecute(lambda : self._ExecuteOne(self._sql_find_trader_by_params, params)[0][0])
        if not self._trader_id:
            raise errors.NotAvailableTraderByParams()

    def _CreateTrader(self, params):
        self._trader_id = self.CreateId()
        self._ExecuteOne(self._sql_create_new_trader, self._trader_id, params, self.GetDatetime())

    def _IncreaseProfit(self, profit):
        self._ExecuteOne(self._sql_increase_trader_profit, profit, self._trader_id)

    def _SetTraderStopTime(self):
        self._ExecuteOne(self._sql_set_trader_stoptime, self.GetDatetime(), self._trader_id)

    def _SetTraderStatus(self, status):
        self._ExecuteOne(self._sql_set_trader_status, status, self._trader_id)

    def _SetTraderAsDuring(self):
        self._SetTraderStatus(const.Status.Trader.DURING)

    def _SetTraderAsFinished(self):
        self._SetTraderStatus(const.Status.Trader.FINISHED)

    def _FinishTrader(self):
        if not self._trader_id:
            raise errors.NotAvailableTraderByParams()
        self._SetTraderAsFinished()
        self._SetTraderStopTime()

    # NOTE: Strategy

    def _FindStrategy(self):
        self._strategy_id = common.TryExecute(lambda : self._ExecuteOne(self._sql_find_strategy_for_trader, self._trader_id)[0][0])
        if not self._strategy_id:
            raise errors.NotAvailableStrategyForTrader()

    def _SetStrategyStopTime(self):
        self._ExecuteOne(self._sql_set_strategy_stoptime, self.GetDatetime(), self._strategy_id)

    def _SetStrategyStatus(self, status):
        if not self._strategy_id:
            raise errors.StrategyIsNotCreate()
        self._ExecuteOne(self._sql_set_strategy_status, status, self._strategy_id)

    def _SetStrategyAsInit(self):
        self._SetStrategyStatus(const.Status.Strategy.INIT)

    def _SetStrategyAsTrade(self):
        self._SetStrategyStatus(const.Status.Strategy.TRADE)

    def _SetStrategyProfit(self):
        if not self._strategy_id:
            raise errors.StrategyIsNotCreate()
        if self._GetStrategyProfit and self.GetStrategyStatus() not in (const.Status.Strategy.VOID, const.Status.Strategy.INIT):
            try:
                self._ExecuteOne(self._sql_set_strategy_profit, self._GetStrategyProfit(), self._strategy_id)
            except s_const.errors.NotInitializedStrategy:
                pass

    def _SetStrategyAsComplete(self):
        if not self._strategy_id:
            raise errors.StrategyIsNotCreate()
        self._SetStrategyStatus(const.Status.Strategy.COMPLETE)
        self._SetStrategyStopTime()
        self._strategy_id = None

    # NOTE: Order

    def _FindOrder(self, type, status):
        order_id = self._ExecuteOne(self._sql_find_order_for_strategy, self._strategy_id, type, status)
        if not order_id:
            raise errors.NotAvailableOrderForStrategy()
        return order_id[0][0]

    def _FindInitOrderWait(self):
        self._order_id_I = self._FindOrder(const.Type.Order.INITIAL, const.Status.Order.WAIT)

    def _FindSellOrderWait(self):
        self._order_id_S = self._FindOrder(const.Type.Order.SELL, const.Status.Order.WAIT)

    def _FindBuyOrderWait(self):
        self._order_id_B = self._FindOrder(const.Type.Order.BUY, const.Status.Order.WAIT)

    def _CreateOrder(self, order_id, type):
        self._ExecuteOne(self._sql_create_order_for_strategy, order_id, self._strategy_id, type, self.GetDatetime())
        return order_id

    def _CreateInitOrder(self, order_id):
        self._order_id_I = self._CreateOrder(order_id, const.Type.Order.INITIAL)

    def _CreateSellOrder(self, order_id):
        self._order_id_S = self._CreateOrder(order_id, const.Type.Order.SELL)

    def _CreateBuyOrder(self, order_id):
        self._order_id_B = self._CreateOrder(order_id, const.Type.Order.BUY)

    def _SetOrderAsCompleted(self, id):
        trueview = common.TryExecute(common.Lambda(self._GetOrderTrueview, id))
        self._ExecuteOne(self._sql_complete_order_for_strategy, trueview, self.GetDatetime(), id)

    def _CompleteInitOrder(self):
        if not self._order_id_I:
            raise errors.OrderIsNotCreate()
        self._SetOrderAsCompleted(self._order_id_I)
        # note: if the initial-order is closed, then the trading-strategy has already been formed
        self.UpdateStrategyPreview()
        self._order_id_I = None

    def _CompleteSellOrder(self):
        if not self._order_id_S:
            raise errors.OrderIsNotCreate()
        self._SetOrderAsCompleted(self._order_id_S)
        self._order_id_S = None

    def _CompleteBuyOrder(self):
        if not self._order_id_B:
            raise errors.OrderIsNotCreate()
        self._SetOrderAsCompleted(self._order_id_B)
        self._order_id_B = None

    def _SetOrderAsCancelled(self, id):
        trueview = common.TryExecute(common.Lambda(self._GetOrderTrueview, id))
        self._ExecuteOne(self._sql_cancel_order_for_strategy, trueview, self.GetDatetime(), id)

    # NOTE: DB

    def _FinishCurrentStrategy(self):
        self.UpdateStrategyRecoverystring()
        self.UpdateStrategyPreview()
        self._SetStrategyProfit()
        common.TryExecute(self.CancelInitOrder, errors.OrderIsNotCreate)
        common.TryExecute(self._CompleteSellOrder, errors.OrderIsNotCreate)
        common.TryExecute(self.CancelBuyOrder, errors.OrderIsNotCreate)
        common.TryExecute(self._IncreaseProfit(self.GetStrategyProfit()))
        self._SetStrategyAsComplete()

    def RegGetStrategyRecoverystring(self, call_object):
        self._GetStrategyRecoverystring = call_object

    def RegGetStrategyPreview(self, call_object):
        self._GetStrategyPreview = call_object

    def RegGetStrategyProfit(self, call_object):
        self._GetStrategyProfit = call_object

    def RegGetOrderTrueview(self, call_object):
        self._GetOrderTrueview = call_object

    # brief: initialize BD for a trader
    # param: db_filepath - full file path to save BD
    def Init(self, db_filepath, params):
        self._db_filepath = db_filepath
        self._CreatesDB()
        common.Execute1Or2(common.Lambda(self._FindTrader, params), errors.NotAvailableTraderByParams, common.Lambda(self._CreateTrader, params))
        common.Execute1Or2(common.Lambda(self._FindStrategy), errors.NotAvailableStrategyForTrader, common.Lambda(self.CreateNewStrategy))
        common.TryExecute(common.Lambda(self._FindInitOrderWait), errors.NotAvailableOrderForStrategy)
        common.TryExecute(common.Lambda(self._FindSellOrderWait), errors.NotAvailableOrderForStrategy)
        common.TryExecute(common.Lambda(self._FindBuyOrderWait), errors.NotAvailableOrderForStrategy)
        self.UpdateStrategyRecoverystring()
        self.UpdateStrategyPreview()

    # brief: initialize new trading for trader
    # param: init_order_id - initial order id from which trading begins
    def InitNewTrading(self, init_order_id):
        self._FinishCurrentStrategy()
        self.CreateNewStrategy()
        self._SetTraderAsDuring()
        self.SetInitOrder(init_order_id)

    # NOTE: Trader

    def GetId(self):
        if not self._trader_id:
            raise errors.TraderIsNotCreate()
        return self._trader_id

    def GetPtofit(self):
        if not self._trader_id:
            raise errors.TraderIsNotCreate()
        return float(self._ExecuteOne(self._sql_get_trader_profit, self._trader_id)[0][0])

    def GetStatus(self):
        if not self._trader_id:
            raise errors.TraderIsNotCreate()
        return self._ExecuteOne(self._sql_get_trader_status, self._trader_id)[0][0]

    def GetCompletedStrategy(self):
        if not self._trader_id:
            raise errors.TraderIsNotCreate()
        return int(self._ExecuteOne(self._sql_get_trader_completed_strategy_quantity, self._trader_id)[0][0])

    def GetCompletedStrategyForTrader(self, trader_id):
        if not self._IsTraderExistByID(trader_id):
            raise errors.TraderIsNotExist()
        return int(self._ExecuteOne(self._sql_get_trader_completed_strategy_quantity, trader_id)[0][0])

    def Finish(self):
        if not self._trader_id:
            raise errors.TraderIsNotCreate()
        common.TryExecute(self._FinishCurrentStrategy, errors.StrategyIsNotCreate)
        self._FinishTrader()

    # NOTE: Strategy

    def CreateNewStrategy(self):
        self._strategy_id = self.CreateId()
        self._ExecuteOne(self._sql_create_new_strategy_for_trader, self._strategy_id, self._trader_id, self.GetDatetime())

    def GetStrategyId(self):
        if not self._strategy_id:
            raise errors.StrategyIsNotCreate()
        return self._strategy_id

    def SetStrategyAsWait(self):
        if not self._strategy_id:
            raise errors.StrategyIsNotCreate()
        self._SetStrategyStatus(const.Status.Strategy.WAIT)

    def GetStrategyRecovery(self):
        if not self._strategy_id:
            raise errors.StrategyIsNotCreate()
        return self._ExecuteOne(self._sql_get_strategy_recovery_string, self._strategy_id)[0][0]

    def GetStrategyPreview(self):
        if not self._strategy_id:
            raise errors.StrategyIsNotCreate()
        return self._ExecuteOne(self._sql_get_strategy_preview_string, self._strategy_id)[0][0]

    def GetStrategyProfit(self):
        if not self._strategy_id:
            raise errors.StrategyIsNotCreate()
        return float(self._ExecuteOne(self._sql_get_strategy_profit, self._strategy_id)[0][0])

    def GetStrategyStatus(self):
        if not self._strategy_id:
            raise errors.StrategyIsNotCreate()
        return self._ExecuteOne(self._sql_get_strategy_status, self._strategy_id)[0][0]

    def UpdateStrategyPreview(self):
        if not self._strategy_id:
            raise errors.StrategyIsNotCreate()
        if self._GetStrategyPreview:
            try:
                self._ExecuteOne(self._sql_set_strategy_preview_string, self._GetStrategyPreview(), self._strategy_id)
            except s_const.errors.NotInitializedStrategy:
                pass

    def UpdateStrategyRecoverystring(self):
        if not self._strategy_id:
            raise errors.StrategyIsNotCreate()
        if self._GetStrategyRecoverystring:
            try:
                self._ExecuteOne(self._sql_set_strategy_recovery_string, self._GetStrategyRecoverystring(), self._strategy_id)
            except s_const.errors.NotInitializedStrategy:
                pass

    def FinishStrategy(self):
        self._FinishCurrentStrategy()
        self._SetTraderAsDuring()
        return self.GetCompletedStrategy()

    # NOTE: Order

    def CancelInitOrder(self):
        if not self._order_id_I:
            raise errors.OrderIsNotCreate()
        self._SetOrderAsCancelled(self._order_id_I)
        self._order_id_I = None

    def CancelSellOrder(self):
        if not self._order_id_S:
            raise errors.OrderIsNotCreate()
        self._SetOrderAsCancelled(self._order_id_S)
        self._order_id_S = None

    def CancelBuyOrder(self):
        if not self._order_id_B:
            raise errors.OrderIsNotCreate()
        self._SetOrderAsCancelled(self._order_id_B)
        self._order_id_B = None

    def SetInitOrder(self, order_id):
        common.TryExecute(self._CompleteInitOrder, errors.OrderIsNotCreate)
        common.TryExecute(self._CompleteSellOrder, errors.OrderIsNotCreate)
        common.TryExecute(self.CancelBuyOrder, errors.OrderIsNotCreate)
        self._CreateInitOrder(order_id)
        self._SetStrategyAsInit()
        self._SetTraderAsDuring()
        self.UpdateStrategyRecoverystring()

    def SetSellOrder(self, order_id):
        common.TryExecute(self._CompleteInitOrder, errors.OrderIsNotCreate)
        common.TryExecute(self.CancelSellOrder, errors.OrderIsNotCreate)
        self._CreateSellOrder(order_id)
        self._SetStrategyAsTrade()
        self._SetTraderAsDuring()
        self.UpdateStrategyRecoverystring()

    def SetBuyOrder(self, order_id):
        common.TryExecute(self._CompleteInitOrder, errors.OrderIsNotCreate)
        common.TryExecute(self._CompleteBuyOrder, errors.OrderIsNotCreate)
        self._CreateBuyOrder(order_id)
        self._SetStrategyAsTrade()
        self._SetTraderAsDuring()
        self.UpdateStrategyRecoverystring()

    def GetInitOrder(self):
        if not self._order_id_I:
            raise errors.OrderIsNotCreate()
        return self._order_id_I

    def GetSellOrder(self):
        if not self._order_id_S:
            raise errors.OrderIsNotCreate()
        return self._order_id_S

    def GetBuyOrder(self):
        if not self._order_id_B:
            raise errors.OrderIsNotCreate()
        return self._order_id_B

    @classmethod
    def GetDatetime(cls):
        return datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")

    @classmethod
    def CreateId(cls, length=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    _sql_create_table_Trader = \
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
"""

    _sql_create_table_Strategy = \
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
"""

    _sql_create_table_Order = \
"""
-- brief: table for presenting one trade-order on the Exchange
CREATE TABLE IF NOT EXISTS "Order"
(
id              TEXT    NOT NULL,                    -- order identificator
id_s            TEXT    NOT NULL,                    -- identificator of master-trader
type            TEXT    NOT NULL,                    -- order type
status          TEXT    NOT NULL DEFAULT "wait",     -- order status
truview         TEXT    NULL,                        -- order truview-string
time_start      TEXT    NULL,                        -- time of opening order
time_stop       TEXT    NULL,                        -- time of closing order
PRIMARY KEY("id"),
FOREIGN KEY(id_s) REFERENCES Strategy(id),
CHECK(type in ("initial", "sell", "buy")),
CHECK(status in ("wait", "cancel", "deal"))
);
"""

# NOTE: Trader

    _sql_find_trader_by_params = \
"""
SELECT id FROM "Trader" WHERE params=?1 AND status!="finished";
"""

    _sql_create_new_trader = \
"""
INSERT INTO "Trader" (id, params, time_start) VALUES (?1, ?2, ?3);
"""

    _sql_get_trader_status = \
"""
SELECT status FROM "Trader" WHERE id=?1;
"""

    _sql_get_trader_profit = \
"""
SELECT profit FROM "Trader" WHERE id=?1;
"""

    _sql_get_trader_completed_strategy_quantity = \
"""
SELECT COUNT(*) FROM Strategy WHERE id_t=?1 AND status="complete";
"""
    
    _sql_get_trader_quantity_by_id = \
"""
SELECT COUNT(*) FROM Trader WHERE id=?1;
"""

    _sql_increase_trader_profit = \
"""
UPDATE "Trader" SET profit=(?1+(SELECT profit FROM "Trader" WHERE id=?2)) WHERE id=?2;
"""

    _sql_set_trader_stoptime = \
"""
UPDATE "Trader" SET time_stop=?1 WHERE id=?2;
"""

    _sql_set_trader_status = \
"""
UPDATE "Trader" SET status=?1 WHERE id=?2;
"""

# NOTE: Strategy

    _sql_find_strategy_for_trader = \
"""
SELECT id FROM "Strategy" WHERE id_t=?1 AND status NOT IN ("complete");
"""

    _sql_create_new_strategy_for_trader = \
"""
INSERT INTO "Strategy" (id, id_t, time_start) VALUES (?1, ?2, ?3);
"""

    _sql_set_strategy_status = \
"""
UPDATE "Strategy" SET status=?1 WHERE id=?2;
"""

    _sql_set_strategy_stoptime = \
"""
UPDATE "Strategy" SET time_stop=?1 WHERE id=?2;
"""

    _sql_set_strategy_recovery_string = \
"""
UPDATE "Strategy" SET recovery=?1 WHERE id=?2;
"""

    _sql_set_strategy_preview_string = \
"""
UPDATE "Strategy" SET preview=?1 WHERE id=?2;
"""

    _sql_set_strategy_profit = \
"""
UPDATE "Strategy" SET profit=?1 WHERE id=?2;
"""

    _sql_get_strategy_status = \
"""
SELECT status FROM "Strategy" WHERE id=?1;
"""

    _sql_get_strategy_recovery_string = \
"""
SELECT recovery FROM "Strategy" WHERE id=?1;
"""

    _sql_get_strategy_preview_string = \
"""
SELECT preview FROM "Strategy" WHERE id=?1;
"""

    _sql_get_strategy_profit = \
"""
SELECT profit FROM "Strategy" WHERE id=?1;
"""

# NOTE: Order

    _sql_find_order_for_strategy = \
"""
SELECT id FROM "Order" WHERE id_s=?1 AND type=?2 AND status=?3;
"""

    _sql_create_order_for_strategy = \
"""
INSERT INTO "Order" (id, id_s, type, time_start) VALUES (?1, ?2, ?3, ?4);
"""

    _sql_complete_order_for_strategy = \
"""
UPDATE "Order" SET status="deal", truview=?1, time_stop=?2 WHERE id=?3;
"""

    _sql_cancel_order_for_strategy = \
"""
UPDATE "Order" SET status="cancel", truview=?1, time_stop=?2 WHERE id=?3;
"""
