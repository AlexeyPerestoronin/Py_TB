import string
import random
import sqlite3
import datetime

import common

import trader.data_base.tables as table
import trader.data_base.tables.consts as table_const
import trader.data_base.tables.errors as table_error

# brief: implements logic of DB controlling for trading
class DbSimple(table.Base):
    def __init__(self):
        # data-base(s)
        table.Base.__init__(self)
        self._db_filepath = None
        self._params = None
        self._trader = table.Trader()
        self._strategy = table.Strategy()
        self._order_I = table.Order()
        self._order_S = table.Order()
        self._order_B = table.Order()

    # NOTE: Set..

    def SetParams(self, params):
        self._params = params

    def SetFilePath(self, db_filepath):
        table.Base.SetFilePath(self, db_filepath)
        self._db_filepath = db_filepath

    # NOTE: SetCallback...

    def SetCallbackGetStrategyRecoverystring(self, call_object):
        self._strategy.SetCallbackGetStrategyRecoverystring(call_object)

    def SetCallbackGetStrategyPreview(self, call_object):
        self._strategy.SetCallbackGetStrategyPreview(call_object)

    def SetCallbackGetStrategyProfit(self, call_object):
        self._strategy.SetCallbackGetStrategyProfit(call_object)

    def SetCallbackGetOrderTrueview(self, call_object):
        self._order_I.SetCallbackGetOrderTrueview(call_object)
        self._order_S.SetCallbackGetOrderTrueview(call_object)
        self._order_B.SetCallbackGetOrderTrueview(call_object)

    # brief: initialize BD for a trading
    def Init(self):
        # step 1: initialize trader
        self._trader.SetParams(self._params)
        self._trader.SetFilePath(self._db_filepath)
        self._trader.Init()
        common.Execute1Or2(self._trader.Find, table_error.NotAvailableTraderByParams, self._trader.Create)
        # step 2: initialize strategy
        self._strategy.SetFilePath(self._db_filepath)
        self._strategy.SetTraderId(self._trader.GetId())
        self._strategy.Init()
        common.Execute1Or2(self._strategy.Find, table_error.NotAvailableStrategyForTrader, self._strategy.Create)
        # step 3: initialize initial-order
        self._order_I.SetFilePath(self._db_filepath)
        self._order_I.SetStrategyId(self._strategy.GetId())
        self._order_I.SetType(table_const.Type.Order.INITIAL)
        self._order_I.SetStatus(table_const.Status.Order.WAIT)
        self._order_I.Init()
        common.TryExecute(self._order_I.Find, table_error.NotAvailableOrderForStrategy)
        # step 4: initialize sell-order
        self._order_S.SetFilePath(self._db_filepath)
        self._order_S.SetStrategyId(self._strategy.GetId())
        self._order_S.SetType(table_const.Type.Order.SELL)
        self._order_S.SetStatus(table_const.Status.Order.WAIT)
        self._order_S.Init()
        common.TryExecute(self._order_S.Find, table_error.NotAvailableOrderForStrategy)
        # step 5: initialize buy-order
        self._order_B.SetFilePath(self._db_filepath)
        self._order_B.SetStrategyId(self._strategy.GetId())
        self._order_B.SetType(table_const.Type.Order.BUY)
        self._order_B.SetStatus(table_const.Status.Order.WAIT)
        self._order_B.Init()
        common.TryExecute(self._order_B.Find, table_error.NotAvailableOrderForStrategy)

    # brief: initialize new trading for trader
    # param: init_order_id - initial order id from which trading begins
    def InitNewTrading(self, init_order_id):
        self.FinishCurrentStrategy()
        self.CreateNewStrategy()
        self.SetInitOrder(init_order_id)

    def Update(self):
        common.TryExecute(self._strategy.Update)
        common.TryExecute(self._order_I.Update)
        common.TryExecute(self._order_S.Update)
        common.TryExecute(self._order_B.Update)

    # NOTE: Trader: ...

    def FinishTrader(self):
        self._trader.Check()
        if self._strategy.Is():
            self.FinishCurrentStrategy()
        self._trader.Finish()

    # NOTE: Trader: Get...

    def GetTraderId(self):
        return self._trader.GetId()

    def GetTraderPtofit(self):
        return self._trader.GetPtofit()

    def GetTraderStatus(self):
        return self._trader.GetStatus()

    def GetTraderCompletedStrategy(self):
        trader_id = self._trader.GetId()
        return int(self._ExecuteOne('SELECT COUNT(*) FROM Strategy WHERE id_t=?1 AND status="complete";', trader_id)[0][0])

    # NOTE: Strategy: ...

    def FinishCurrentStrategy(self):
        common.TryExecute(self._order_I.Cancel, table_error.OrderIsNotCreate)
        common.TryExecute(self._order_S.Deal, table_error.OrderIsNotCreate)
        common.TryExecute(self._order_B.Cancel, table_error.OrderIsNotCreate)
        current_strategy_profit = self._strategy.Finish()
        self._trader.IncreaseProfit(current_strategy_profit)
        self._trader.SetAsDuring()

    def CreateNewStrategy(self):
        if self._strategy.Is():
            self.FinishCurrentStrategy()
        self._strategy.Create()
        self._trader.SetAsDuring()

    # NOTE: Strategy: Set...

    def SetStrategyAsWait(self):
        self._strategy.SetAsWait()

    # NOTE: Strategy: Get...

    def GetStrategyId(self):
        self._strategy.GetId()

    def GetStrategyRecovery(self):
        return self._strategy.GetRecovery()

    def GetStrategyPreview(self):
        return self._strategy.GetPreview()

    def GetStrategyProfit(self):
        return self._strategy.GetProfit()

    def GetStrategyStatus(self):
        return self._strategy.GetStatus()

    # NOTE: Order: Set...

    def SetInitOrder(self, order_id):
        common.TryExecute(self._order_I.Deal, table_error.OrderIsNotCreate)
        common.TryExecute(self._order_S.Deal, table_error.OrderIsNotCreate)
        common.TryExecute(self._order_B.Cancel, table_error.OrderIsNotCreate)
        self._order_I.Create(order_id)
        self._strategy.SetAsInit()
        self._trader.SetAsDuring()
        self.Update()

    def SetSellOrder(self, order_id):
        common.TryExecute(self._order_I.Deal, table_error.OrderIsNotCreate)
        common.TryExecute(self._order_S.Cancel, table_error.OrderIsNotCreate)
        self._order_S.Create(order_id)
        self._strategy.SetAsTrade()
        self._trader.SetAsDuring()
        self.Update()

    def SetBuyOrder(self, order_id):
        common.TryExecute(self._order_I.Deal, table_error.OrderIsNotCreate)
        common.TryExecute(self._order_B.Deal, table_error.OrderIsNotCreate)
        self._order_B.Create(order_id)
        self._strategy.SetAsTrade()
        self._trader.SetAsDuring()
        self.Update()

    # NOTE: Order: Get...

    def GetInitOrder(self):
        return self._order_I.GetId()

    def GetSellOrder(self):
        return self._order_S.GetId()

    def GetBuyOrder(self):
        return self._order_B.GetId()

    # NOTE: Order: Cancell

    def CancelInitOrder(self):
        common.TryExecute(self._order_I.Cancel, table_error.OrderIsNotCreate)

    def CancelSellOrder(self):
        common.TryExecute(self._order_S.Cancel, table_error.OrderIsNotCreate)

    def CancelBuyOrder(self):
        common.TryExecute(self._order_B.Cancel, table_error.OrderIsNotCreate)
