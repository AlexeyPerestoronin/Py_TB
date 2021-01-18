import os
import json
import copy
import time
import sqlite3
import datetime

import common.faf as faf
import common.log as log

import trader.db as db
import trader.const.errors as error

import strategy
import strategy.stairs as ss
import strategy.const as s_const
import strategy.const.errors as s_error

# brief: implements simple logic for trading
class Simple:
    def __init__(self, connection, strategy):
        if not (isinstance(strategy, ss.Simple) or isinstance(strategy, ss.Dependency)):
            raise error.UnavailableTradeStrategyForTrader()
        # settings for self (for trader)
        self._connection = connection
        self._strategy = strategy
        self._db = db.Simple()
        # settings for exchange
        self._pair = None
        # settings for trade-strategy
        self._init_cost = None
        # setting for saving trading state
        self._save_catalog = None
        self._db_filepath = None
        self._log_preview = None

    # brief: saves preview of trading-strategy that is realizing now
    def _SaveTradingPreview(self):
        strategy.StrategyPreview(self._strategy).SavePreviewInFile(self._log_preview)

    # brief: sets sell and buy orders for current step of trade-strategy
    def _SetOrders(self):
        self._db.SetSellOrderId(self._connection.CreateOrder_Sell(self._pair, self._strategy.GetSellQuantity(), self._strategy.GetSellRate()))
        self._db.SetBuyOrderId(self._connection.CreateOrder_Buy(self._pair, self._strategy.GetBuyQuantity(), self._strategy.GetBuyRate()))

    # brief: initializes new trading
    def _InitNewTrading(self):
        self._db.InitNewTrading(self._connection.CreateOrder_BuyMarketTotal(self._pair, self._init_cost))

    # brief: initializes trading
    def _InitTrading(self):
        initial_order_id = self._db.GetInitialOrderId()
        if self._connection.IsOrderCancel(initial_order_id):
            self._db.SetAsComplete()
        elif self._connection.IsOrderComplete(self._pair, initial_order_id):
            if self._strategy.GetStep():
                self._strategy = self._strategy.ComputeToStep(1)
            self._strategy.SetQuantityPrecision1(self._connection.GetQuantityPrecisionForPair(self._pair))
            self._strategy.SetPricePrecision1(self._connection.GetPricePrecisionForPair(self._pair))
            self._strategy.SetCommissionSell(self._connection.GetTakerCommission(self._pair))
            self._strategy.SetCommissionBuy(self._connection.GetTakerCommission(self._pair))
            initial_order_rate = self._connection.GetOrderRate(initial_order_id)
            initial_order_cost = self._connection.GetOrderCost2(initial_order_id)
            self._strategy.Init(initial_order_rate, initial_order_cost)
            self._db.SaveStrategy(self._strategy.CreateRecoveryString())
            # TODO: trading preview need save in DB
            self._SaveTradingPreview()
            self._SetOrders()

    # brief: iterates initialized trading
    def _IterateTrading(self):
        trading_result = False
        try:
            sell_order_id = self._db.GetSellOrderId()
            buy_order_id = self._db.GetBuyOrderId()
            is_sell_open = self._connection.IsOrderOpen(sell_order_id)
            is_buy_open = self._connection.IsOrderOpen(buy_order_id)
            if not is_sell_open and is_buy_open:
                self._connection.CancelOrder(buy_order_id)
                self._db.SetAsComplete()
                trading_result = True
            elif not is_buy_open and is_sell_open:
                self._connection.CancelOrder(sell_order_id)
                self._strategy = self._strategy.ComputeNextStep()
                self._db.SaveStrategy(self._strategy.CreateRecoveryString())
                self._SetOrders()
            elif not is_buy_open and not is_sell_open:
                is_sell_complete = self._connection.IsOrderComplete(self._pair, sell_order_id)
                is_buy_complete = self._connection.IsOrderComplete(self._pair, buy_order_id)
                if is_sell_complete and is_buy_complete:
                    reinitial_rate = self._connection.GetOrderRate(buy_order_id)
                    reinitial_cost = self._connection.GetOrderCost2(buy_order_id)
                    self._strategy = self._strategy.ComputeToStep(1)
                    self._db.SaveStrategy(self._strategy.CreateRecoveryString())
                    self._strategy.Init(reinitial_rate, reinitial_cost)
                    self._SaveTradingPreview()
                    self._SetOrders()
                elif is_sell_complete and not is_buy_complete:
                    self._db.SetAsComplete()
                    trading_result = True
                elif is_buy_complete and not is_sell_complete:
                    self._strategy = self._strategy.ComputeNextStep()
                    self._db.SaveStrategy(self._strategy.CreateRecoveryString())
                    self._SetOrders()
                else:
                    # in this case a user cancelled all orders manually
                    self._db.SetAsComplete()
                    trading_result = True
        except s_error.ExceededAvailableCurrency:
            # TODO: need realize wait-logic
            pass
        return trading_result

    # brief: performing one trading iteration
    def Iterate(self):
        try:
            self._db.Init(self._db_filepath)
            if self._db.IsInit():
                self._InitTrading()
            elif self._db.IsTrade():
                self._strategy = type(self._strategy).RestoreFromRecoveryString(self._db.RestoreStrategy())
                self._IterateTrading()
            elif self._db.IsComplete():
                self._InitNewTrading()
            # elif self._db.IsWaite():
            #     pass
        except error.NotAvailableTrading:
            self._InitNewTrading()

    # brief: sets currency-pair for trading
    # param: pair - target currency-pair
    def SetPair(self, pair):
        self._pair = pair

    # brief: sets initial cost for trading
    # param: init_cost - target initial cost
    def SetInitCost(self, init_cost):
        self._init_cost = init_cost

    # brief: trading initialization
    # param: save_catalog - a catalog name in which will saving all trading's files
    def SetSaveCatalog(self, save_catalog):
        self._save_catalog = save_catalog
        faf.CreateDirectory(self._save_catalog)
        self._db_filepath = os.path.join(self._save_catalog, "db.sqlite")
        self._log_preview = os.path.join(self._save_catalog, "strategy.preview.txt")

    # brief: finishing trading
    def Finish(self):
        directory, catalogname_old = faf.SplitPath3(self._save_catalog)
        catalogname_new = catalogname_old + "-COMPLETE({})".format(datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
        faf.RenameFile(directory, catalogname_old, catalogname_new)
        return os.path.join(directory, catalogname_new)
