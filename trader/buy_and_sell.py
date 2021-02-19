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
import strategy.const.errors as strategy_error

class BuyAndSell(trader.BaseSTrader):
    def __init__(self):
        trader.BaseSTrader.__init__(self)

    def _GetStrategyProfit(self):
        if self._strategy.IsInitialized():
            return self._strategy.GetStepProfitLeft()
        raise strategy_error.NotInitializedStrategy()

    def _SetOrders(self):
        self._db.SetSellOrder(self._connection.CreateOrder_Sell(self._pair, self._strategy.GetSellQuantity(), self._strategy.GetSellRate()))
        self._db.SetBuyOrder(self._connection.CreateOrder_Buy(self._pair, self._strategy.GetBuyQuantity(), self._strategy.GetBuyRate()))

    def _FinishTrading(self):
        self._db.FinishCurrentStrategy()
        if self._completed_policy.Check():
            self._db.CreateNewStrategy()
        else:
            self._db.FinishTrader()

    def _WaitTrading(self):
        sell_order_id = self._db.GetSellOrder()
        if self._connection.IsOrderCancel(sell_order_id) or self._connection.IsOrderComplete(self._pair, sell_order_id):
            self._db.CancelSellOrder()
            self._FinishTrading()

    def _InitNewTrading(self):
        self._db.SetInitOrder(self._connection.CreateOrder_BuyMarketTotal(self._pair, self._init_cost))

    def _ReinitCurrentTrading(self):
        initial_order_id = self._db.GetInitOrder()
        if self._connection.IsOrderCancel(initial_order_id):
            self._FinishTrading()
        elif self._connection.IsOrderComplete(self._pair, initial_order_id):
            self._PreinitStrategy()
            initial_order_rate = self._connection.GetOrderRate(initial_order_id)
            initial_order_cost = self._connection.GetOrderCost2(initial_order_id)
            self._strategy.Init(initial_order_rate, initial_order_cost)
            self._SetOrders()

    def _IterateTrading(self):
        self._strategy = type(self._strategy).RestoreFromRecoveryString(self._db.GetStrategyRecovery())
        try:
            sell_order_id = self._db.GetSellOrder()
            buy_order_id = self._db.GetBuyOrder()
            is_sell_open = self._connection.IsOrderOpen(sell_order_id)
            is_buy_open = self._connection.IsOrderOpen(buy_order_id)
            if not is_sell_open and is_buy_open:
                self._connection.CancelOrderFull(buy_order_id)
                self._FinishTrading()
            elif not is_buy_open and is_sell_open:
                self._connection.CancelOrderFull(sell_order_id)
                self._strategy = self._strategy.ComputeNextStep()
                self._SetOrders()
            elif not is_buy_open and not is_sell_open:
                is_sell_complete = self._connection.IsOrderComplete(self._pair, sell_order_id)
                is_buy_complete = self._connection.IsOrderComplete(self._pair, buy_order_id)
                if is_sell_complete and is_buy_complete:
                    new_initial_rate = self._connection.GetOrderRate(buy_order_id)
                    new_initial_cost = self._connection.GetOrderCost2(buy_order_id)
                    self._PreinitStrategy()
                    self._strategy.Init(new_initial_rate, new_initial_cost)
                    self._SetOrders()
                elif is_buy_complete and not is_sell_complete:
                    self._strategy = self._strategy.ComputeNextStep()
                    self._SetOrders()
                elif is_sell_complete and not is_buy_complete:
                    self._FinishTrading()
                else:
                    raise trader_error.UserCancelOrdersManual()
        except strategy_error.ExceededAvailableCurrency as eac_error:
            self._db.CancelBuyOrder()
            sell_rate = eac_error.GetSellRate()
            sell_quantity = eac_error.GetSellQuantity()
            self._db.SetSellOrder(self._connection.CreateOrder_Sell(self._pair, sell_quantity, sell_rate))
            self._db.SetStrategyAsWait()
