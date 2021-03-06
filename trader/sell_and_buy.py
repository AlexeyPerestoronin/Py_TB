import os
import json

import connection.const.errors as connection_error

import trader
import trader.consts as trader_const
import trader.errors as trader_error
import trader.data_base as db
import trader.completed_policy as trader_cp
import trader.data_base.tables.errors as table_error
import trader.data_base.tables.consts as table_const

import strategy
import strategy.stairs as ss
import strategy.stairs.sell_and_buy
import strategy.const.errors as strategy_error

class SellAndBuy(trader.BuyAndSell):
    def __init__(self):
        trader.BaseTrader.__init__(self)

    def _CheckStrategyClass(self):
        if isinstance(self._strategy, ss.sell_and_buy.StairsSellBuy):
            return
        raise trader_error.UnavailableTradeStrategyForTrader()

    def _GetStrategyProfit(self):
        if self._strategy.IsInitialized():
            return self._strategy.GetStepProfitRight()
        raise strategy_error.NotInitializedStrategy()

    def _SetOrders(self):
        self._db.SetBuyOrder(self._connection.CreateOrder_Buy(self._pair, self._strategy.GetBuyQuantity(), self._strategy.GetBuyRate()))
        self._db.SetSellOrder(self._connection.CreateOrder_Sell(self._pair, self._strategy.GetSellQuantity(), self._strategy.GetSellRate()))

    def _WaitTrading(self):
        buy_order_id = self._db.GetBuyOrder()
        if self._connection.IsOrderCancel(buy_order_id) or self._connection.IsOrderComplete(self._pair, buy_order_id):
            self._db.CancelSellOrder()
            self._FinishTrading()

    def _InitNewTrading(self):
        self._db.SetInitOrder(self._connection.CreateOrder_SellMarket(self._pair, self._init_cost))

    def _ReinitCurrentTrading(self):
        initial_order_id = self._db.GetInitOrder()
        if self._connection.IsOrderCancel(initial_order_id):
            self._FinishTrading()
        elif self._connection.IsOrderComplete(self._pair, initial_order_id):
            self._PreinitStrategy()
            initial_order_rate = self._connection.GetOrderRate(initial_order_id)
            self._strategy.SetInitRate(initial_order_rate)
            initial_order_quantity = self._connection.GetOrderCostLeft(initial_order_id)
            self._strategy.SetInitQuantity(initial_order_quantity)
            self._strategy.Init()
            self._SetOrders()

    def _IterateTrading(self):
        self._strategy = type(self._strategy).RestoreFromRecoveryString(self._db.GetStrategyRecovery())
        try:
            buy_order_id = self._db.GetBuyOrder()
            sell_order_id = self._db.GetSellOrder()
            is_sell_open = self._connection.IsOrderOpen(buy_order_id)
            is_buy_open = self._connection.IsOrderOpen(sell_order_id)
            if not is_buy_open and is_sell_open:
                self._connection.CancelOrderFull(sell_order_id)
                self._FinishTrading()
            elif not is_sell_open and is_buy_open:
                self._connection.CancelOrderFull(buy_order_id)
                self._strategy = self._strategy.ComputeNextStep()
                self._SetOrders()
            elif not is_sell_open and not is_buy_open:
                is_buy_complete = self._connection.IsOrderComplete(self._pair, buy_order_id)
                is_sell_complete = self._connection.IsOrderComplete(self._pair, sell_order_id)
                if is_sell_complete and is_buy_complete:
                    self._PreinitStrategy()
                    new_initial_rate = self._connection.GetOrderRate(sell_order_id)
                    self._strategy.SetInitRate(new_initial_rate)
                    new_initial_quantity = self._connection.GetOrderCostLeft(sell_order_id)
                    self._strategy.SetInitQuantity(new_initial_quantity)
                    self._strategy.Init()
                    self._SetOrders()
                elif is_sell_complete and not is_buy_complete:
                    self._strategy = self._strategy.ComputeNextStep()
                    self._SetOrders()
                elif is_buy_complete and not is_sell_complete:
                    self._FinishTrading()
                else:
                    raise trader_error.UserCancelOrdersManual()
        except strategy_error.ExceededAvailableCurrency as eac_error:
            self._db.CancelSellOrder()
            buy_rate = eac_error.GetBuyRate()
            buy_quantity = eac_error.GetBuyQuantity()
            self._db.SetSellOrder(self._connection.CreateOrder_Buy(self._pair, buy_quantity, buy_rate))
            self._db.SetStrategyAsWait()

    @classmethod
    def GetID(cls):
        return trader_const.IDs.SELL_AND_BUY.Key
