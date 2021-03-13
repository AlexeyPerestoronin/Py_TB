import os
import json

import connection.const.errors as connection_error

import trader.consts as trader_const
import trader.errors as trader_error
import trader.data_base as db
import trader.completed_policy as trader_cp
import trader.data_base.tables.errors as table_error
import trader.data_base.tables.consts as table_const

import strategy

# brief: implements simple logic for trading
class BaseTrader:
    def __init__(self):
        self._trading_params = None
        # class(es)
        self._connection = None
        self._strategy = None
        self._db = None
        self._completed_policy = None
        # self(s)
        self._pair = None
        self._init_cost = None
        self._save_catalog = None
        self._db_filename = None

    # brief: checks if target trade-strategy is possible to realize current trader
    def _CheckStrategyClass(self):
        raise trader_error.MethodIsNotImplemented()

    # brief: checks if target completed-policy is possible to realize current trader
    def _CheckCompletedPolicyClass(self):
        if isinstance(self._completed_policy, trader_cp.InfinityCP):
            return
        raise trader_error.UnavailableCompletedPolicyForTrader()

    # brief: gets recovery-string for the currently realize trade-strategy
    def _GetStrategyRecoverystring(self):
        return self._strategy.CreateRecoveryString()

    # brief: gets preview-string for the currently realize trade-strategy
    def _GetStrategyPreview(self):
        return strategy.StrategyPreview(self._strategy).GetPreview()

    # brief: gets profit for the currently realize trade-strategy
    def _GetStrategyProfit(self):
        trader_error.MethodIsNotImplemented()

    # brief: gets exchange-view for order by its id
    def _GetOrderTrueview(self, order_id):
        try:
            order_deals = self._connection.GetOrderDeals(order_id)
            return json.dumps(order_deals, indent=4)
        except connection_error.OrderIsNotFoundByID as error:
            return str(error)

    # brief: initialize trader settings
    def _InitTraderSettings(self):
        self._pair = self._trading_params[trader_const.SETTINGS.TRADERS.PAIR.Key]
        self._init_cost = self._trading_params[trader_const.SETTINGS.TRADERS.INIT_COST.Key]
        self._db_filename = self._trading_params[trader_const.SETTINGS.TRADERS.DB_FILENAME.Key]
        self._save_catalog = self._trading_params[trader_const.SETTINGS.TRADERS.SAVE_CATALOG.Key]

    # brief: preinitialize trade-strategy
    def _PreinitStrategy(self):
        strategy_settings = self._trading_params[trader_const.SETTINGS.TRADERS.STRATEGY.Key]
        strategy_id = strategy_settings[trader_const.SETTINGS.TRADERS.STRATEGY.ID.Key]
        self._strategy = strategy.DefineStrategy(strategy_id)
        self._CheckStrategyClass()
        strategy_initial_parameters = strategy_settings[trader_const.SETTINGS.TRADERS.STRATEGY.PARAMS.Key]
        self._strategy.SetAllParametersFromDict(strategy_initial_parameters)
        quantity_precision = self._connection.GetQuantityPrecisionForPair(self._pair)
        self._strategy.SetQuantityPrecision(quantity_precision)
        rate_precision = self._connection.GetPricePrecisionForPair(self._pair)
        self._strategy.SetRatePrecision(rate_precision)
        taker_commission = self._connection.GetTakerCommission(self._pair)
        self._strategy.SetCommissionSell(taker_commission)
        self._strategy.SetCommissionBuy(taker_commission)

    # brief: initialize data-base
    def _InitDB(self):
        self._db = db.DbSimple()
        self._db.SetCallbackGetStrategyRecoverystring(self._GetStrategyRecoverystring)
        self._db.SetCallbackGetStrategyPreview(self._GetStrategyPreview)
        self._db.SetCallbackGetStrategyProfit(self._GetStrategyProfit)
        self._db.SetCallbackGetOrderTrueview(self._GetOrderTrueview)
        db_filepath = os.path.join(self._save_catalog, self._db_filename)
        self._db.SetFilePath(db_filepath)
        params = json.dumps(self._trading_params, indent=4)
        self._db.SetParams(params)
        self._db.Init()

    # brief: initialize completed-policy
    def _InitCP(self):
        completed_policy_settings = self._trading_params[trader_const.SETTINGS.TRADERS.COMPLETED_POLICY.Key]
        completed_policy_id = completed_policy_settings[trader_const.SETTINGS.TRADERS.COMPLETED_POLICY.ID.Key]
        self._completed_policy = trader_cp.DefineCompletePolicy(completed_policy_id)
        self._CheckCompletedPolicyClass()
        completed_policy_params = completed_policy_settings[trader_const.SETTINGS.TRADERS.COMPLETED_POLICY.PARAMS.Key]
        self._completed_policy.SetAllParametersFromDict(completed_policy_params)
        self._completed_policy.Init()

    # brief: sets trade-orders for the realizable trading
    def _SetOrders(self):
        raise trader_error.MethodIsNotImplemented()

    # brief: finishes current trade-strategytrading
    def _FinishTrading(self):
        raise trader_error.MethodIsNotImplemented()

    # brief: waite positive course for the current trading
    def _WaitTrading(self):
        raise trader_error.MethodIsNotImplemented()

    # brief: initializes new trading
    def _InitNewTrading(self):
        raise trader_error.MethodIsNotImplemented()

    # brief: re-initializes current trading
    def _ReinitCurrentTrading(self):
        raise trader_error.MethodIsNotImplemented()

    # brief: iterates initialized trading
    def _IterateTrading(self):
        raise trader_error.MethodIsNotImplemented()

    # NOTE: Set...

    def SetConnection(self, connection):
        self._connection = connection

    def SetParameters(self, params):
        self._trading_params = params

    # NOTE: ...

    # brief: initialize trader
    def Init(self):
        self._InitTraderSettings()
        self._PreinitStrategy()
        self._InitDB()
        self._InitCP()

    # brief: performing one trading iteration
    def Iterate(self):
        try:
            current_trader_status = self._db.GetTraderStatus()
            if current_trader_status == table_const.Status.Trader.VOID:
                self._InitNewTrading()
            elif current_trader_status == table_const.Status.Trader.DURING:
                current_strategy_status = self._db.GetStrategyStatus()
                if current_strategy_status == table_const.Status.Strategy.VOID:
                    self._InitNewTrading()
                elif current_strategy_status == table_const.Status.Strategy.INIT:
                    self._ReinitCurrentTrading()
                elif current_strategy_status == table_const.Status.Strategy.TRADE:
                    self._IterateTrading()
                elif current_strategy_status == table_const.Status.Strategy.WAIT:
                    self._WaitTrading()
        except table_error.TraderIsNotCreate:
            pass
        except:
            raise trader_error.Trader()

    # brief: gets id of the current class of trader
    # return: id of the current class of trader
    @classmethod
    def GetID(cls):
        return trader_const.IDs.BASE_TRADER.Key
