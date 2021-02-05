import os
import json
import copy
import time
import sqlite3
import datetime

import common.faf as faf
import common.log as log

import trader
import trader.db as db
import trader.completed_policy as t_cp
import trader.const as t_const
import trader.const.errors as error

import strategy
import strategy.stairs as ss
import strategy.const as s_const
import strategy.const.errors as s_error

# brief: implements simple logic for trading
class Simple:
    def __init__(self):
        self._params = None
        self._strategy_params = None
        self._completed_policy_params = None
        # class(es)
        self._connection = None
        self._strategy = None
        self._db = db.Simple()
        self._completed_policy = None
        # self(s)
        self._pair = None
        self._init_cost = None
        self._save_catalog = None
        self._db_filename = None

    def _CheckStrategyClass(self):
        if isinstance(self._strategy, ss.FixedBuyCostS):
            return
        elif isinstance(self._strategy, ss.SoftCostIncreaseS):
            return
        elif isinstance(self._strategy, ss.SoftCostIncreaseD):
            return
        elif isinstance(self._strategy, ss.SoftCostIncreaseDS):
            return
        elif isinstance(self._strategy, ss.FixedBuyCostD):
            return
        elif isinstance(self._strategy, ss.ProgressiveS):
            return
        elif isinstance(self._strategy, ss.ProgressiveD):
            return
        elif isinstance(self._strategy, ss.Dependency):
            return
        elif isinstance(self._strategy, ss.Simple):
            return
        raise error.UnavailableTradeStrategyForTrader()

    def _CheckCompletedPolicyClass(self):
        if isinstance(self._completed_policy, t_cp.FixedCompletedStrategy):
            return
        raise error.UnavailableCompletedPolicyForTrader()

    def _GetStrategyRecoverystring(self):
        if self._strategy.IsInitialized():
            return self._strategy.CreateRecoveryString()
        raise s_const.errors.NotInitializedStrategy()

    def _GetStrategyPreview(self):
        if self._strategy.IsInitialized():
            return strategy.StrategyPreview(self._strategy).GetPreview()
        raise s_const.errors.NotInitializedStrategy()

    def _GetStrategyProfit(self):
        if self._strategy.IsInitialized():
            return self._strategy.GetStepProfit()
        raise s_const.errors.NotInitializedStrategy()

    def _GetOrderTrueview(self, order_id):
        try:
            return json.dumps(self._connection.GetOrderDeals(order_id), indent=4)
        except:
            return "no truview: some error on Exchange side"

    def _PreinitTrader(self):
        self._pair = self._params[t_const.Params.Trading.PAIR]
        self._init_cost = self._params[t_const.Params.Trading.INIT_COST]
        self._db_filename = self._params[t_const.Params.Trading.DB_FILENAME]
        self._save_catalog = self._params[t_const.Params.Trading.SAVE_CATALOG]

    def _PreinitStrategy(self):
        s_key = t_const.Params.Trading.Strategy
        self._strategy = strategy.DefineStrategy(self._strategy_params[s_key.ID])
        self._CheckStrategyClass()
        for key in self._strategy_params.keys():
            if key == s_key.PROFIT:
                self._strategy.SetProfit(self._strategy_params[key])
            elif key == s_key.COEFFICIENT:
                self._strategy.SetCoefficient(self._strategy_params[key])
            elif key == s_key.QUANTITY_PRECISION:
                self._strategy.SetQuantityPrecision1(self._strategy_params[key])
            elif key == s_key.AVAILABLE_CURRENCY:
                self._strategy.SetAvailableCurrency(self._strategy_params[key])
            elif key == s_key.DIFF_SUBCOST:
                self._strategy.SetSubstepsDiffCost(self._strategy_params[key])
            elif key == s_key.ID:
                continue
            else:
                raise error.UndefinedInitStrategyParameter()

    def _InitDB(self):
        self._db.RegGetStrategyRecoverystring(self._GetStrategyRecoverystring)
        self._db.RegGetStrategyPreview(self._GetStrategyPreview)
        self._db.RegGetStrategyProfit(self._GetStrategyProfit)
        self._db.RegGetOrderTrueview(self._GetOrderTrueview)
        self._db.Init(os.path.join(self._save_catalog, self._db_filename), json.dumps(self._params, indent=4))

    def _InitCP(self):
        cp_key = t_const.Params.Trading.CompletedPolicy
        self._completed_policy = t_cp.DefineCompletePolicy(self._completed_policy_params[cp_key.ID])
        self._CheckCompletedPolicyClass()
        self._completed_policy.Init(self._completed_policy_params[cp_key.PARAMS], self._db.GetCompletedStrategy)

    # brief: sets sell and buy orders for current step of trade-strategy
    def _SetOrders(self):
        self._db.SetSellOrder(self._connection.CreateOrder_Sell(self._pair, self._strategy.GetSellQuantity(), self._strategy.GetSellRate()))
        self._db.SetBuyOrder(self._connection.CreateOrder_Buy(self._pair, self._strategy.GetBuyQuantity(), self._strategy.GetBuyRate()))

    def _FinishTrading(self):
        self._db.FinishStrategy()
        if self._completed_policy.Check():
            self._db.CreateNewStrategy()
        else:
            self._db.Finish()

    def _WaitTrading(self):
        sell_order_id = self._db.GetSellOrder()
        if self._connection.IsOrderCancel(sell_order_id) or self._connection.IsOrderComplete(self._params, sell_order_id):
            self._db.CancelSellOrder()
            self._FinishTrading()

    # brief: initializes new trading
    def _InitNewTrading(self):
        self._db.SetInitOrder(self._connection.CreateOrder_BuyMarketTotal(self._pair, self._init_cost))

    # brief: initializes trading
    def _InitTrading(self):
        initial_order_id = self._db.GetInitOrder()
        if self._connection.IsOrderCancel(initial_order_id):
            self._FinishTrading()
        elif self._connection.IsOrderComplete(self._pair, initial_order_id):
            self._PreinitStrategy()
            self._strategy.SetQuantityPrecision1(self._connection.GetQuantityPrecisionForPair(self._pair))
            self._strategy.SetPricePrecision1(self._connection.GetPricePrecisionForPair(self._pair))
            self._strategy.SetCommissionSell(self._connection.GetTakerCommission(self._pair))
            self._strategy.SetCommissionBuy(self._connection.GetTakerCommission(self._pair))
            initial_order_rate = self._connection.GetOrderRate(initial_order_id)
            initial_order_cost = self._connection.GetOrderCost2(initial_order_id)
            self._strategy.Init(initial_order_rate, initial_order_cost)
            self._SetOrders()

    # brief: iterates initialized trading
    def _IterateTrading(self):
        self._strategy = type(self._strategy).RestoreFromRecoveryString(self._db.GetStrategyRecovery())
        try:
            sell_order_id = self._db.GetSellOrder()
            buy_order_id = self._db.GetBuyOrder()
            is_sell_open = self._connection.IsOrderOpen(sell_order_id)
            is_buy_open = self._connection.IsOrderOpen(buy_order_id)
            if not is_sell_open and is_buy_open:
                self._connection.CancelOrder(buy_order_id)
                self._FinishTrading()
            elif not is_buy_open and is_sell_open:
                self._connection.CancelOrder(sell_order_id)
                self._strategy = self._strategy.ComputeNextStep()
                self._SetOrders()
            elif not is_buy_open and not is_sell_open:
                is_sell_complete = self._connection.IsOrderComplete(self._pair, sell_order_id)
                is_buy_complete = self._connection.IsOrderComplete(self._pair, buy_order_id)
                if is_sell_complete and is_buy_complete:
                    new_initial_rate = self._connection.GetOrderRate(buy_order_id)
                    new_initial_cost = self._connection.GetOrderCost2(buy_order_id)
                    self._strategy.GoToStep(1)
                    self._strategy.Init(new_initial_rate, new_initial_cost)
                    self._SetOrders()
                elif is_buy_complete and not is_sell_complete:
                    self._strategy = self._strategy.ComputeNextStep()
                    self._SetOrders()
                elif is_sell_complete and not is_buy_complete:
                    self._FinishTrading()
                else:
                    raise error.UserCancelOrdersManual()
        except s_error.ExceededAvailableCurrency as eac_error:
            self._db.CancelBuyOrder()
            self._db.SetSellOrder(self._connection.CreateOrder_Sell(self._pair, eac_error.GetSellQuantity(), eac_error.GetSellRate()))
            self._db.SetStrategyAsWait()

    def SetConnection(self, connection):
        self._connection = connection

    def SetParameters(self, params):
        self._params = params
        self._strategy_params = self._params["strategy"]
        self._completed_policy_params = self._params["completed_policy"]

    def Init(self):
        self._PreinitTrader()
        self._PreinitStrategy()
        self._InitDB()
        self._InitCP()

    # brief: performing one trading iteration
    def Iterate(self):
        current_trader_status = self._db.GetStatus()
        if current_trader_status == t_const.Status.Trader.VOID:
            self._InitNewTrading()
        elif current_trader_status == t_const.Status.Trader.DURING:
            current_strategy_status = self._db.GetStrategyStatus()
            if current_strategy_status == t_const.Status.Strategy.VOID:
                self._InitNewTrading()
            elif current_strategy_status == t_const.Status.Strategy.INIT:
                self._InitTrading()
            elif current_strategy_status == t_const.Status.Strategy.TRADE:
                self._IterateTrading()
            elif current_strategy_status == t_const.Status.Strategy.WAIT:
                self._WaitTrading()
        elif current_trader_status == t_const.Status.Trader.FINISHED:
            pass
