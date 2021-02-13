import math
import copy
import json
import decimal

import common.faf as faf
import common.precision as c_precision

import strategy.stairs as ss
import strategy.const as const
import strategy.const.errors as error

# brief: implements simple rate-computed strairs trade-strategy
class RCSimple(ss.Simple):
    def __init__(self):
        ss.Simple.__init__(self)

    def _ComputeSellCost(self):
        self._parameters[const.PARAMS.STEP_SELL_COST] = self._PP.DownDecimal(self._parameters[const.PARAMS.STEP_SELL_QUANTITY] * self._parameters[const.PARAMS.STEP_SELL_RATE])
    
    def _ComputeSellProfit(self):
        self._parameters[const.PARAMS.STEP_SELL_PROFIT] = self._parameters[const.PARAMS.STEP_SELL_COST] - self._parameters[const.PARAMS.INIT_COST]

    def _ComputeSellRate(self):
        self._parameters[const.PARAMS.STEP_SELL_RATE] = self.ComputeSellRate(self._parameters[const.PARAMS.STEP_SELL_QUANTITY], self._parameters[const.PARAMS.INIT_COST] * self._parameters[const.PARAMS.GLOBAL_PROFIT])

    def _ComputeSellQuantity(self):
        self._parameters[const.PARAMS.STEP_SELL_QUANTITY] = self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_REAL]

    def _ComputeBuyCost(self):
        self._parameters[const.PARAMS.STEP_BUY_COST] = self._parameters[const.PARAMS.INIT_COST] * self._parameters[const.PARAMS.STEP_COEFFICIENT_1]

    def _ComputeBuyRate(self):
        sell_rate = self._GetNextSellRate()
        self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY] -= self._parameters[const.PARAMS.STEP_BUY_COST]
        if self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY] < 0.:
            raising_error = error.ExceededAvailableCurrency()
            raising_error.SetSellQuantity(self._parameters[const.PARAMS.STEP_SELL_QUANTITY])
            raising_error.SetSellCost(self._parameters[const.PARAMS.STEP_SELL_COST])
            raising_error.SetSellRate(self._parameters[const.PARAMS.STEP_SELL_RATE])
            raise raising_error
        global_sell_commission = self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION]
        global_buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION]
        global_sell_profit = self._parameters[const.PARAMS.GLOBAL_PROFIT]
        total_sell_cost = self._parameters[const.PARAMS.INIT_COST] + self._parameters[const.PARAMS.STEP_BUY_COST]
        step_sell_quantity = self._parameters[const.PARAMS.STEP_SELL_QUANTITY]
        step_buy_cost = self._parameters[const.PARAMS.STEP_BUY_COST]
        step_buy_rate = self._PP.DownDecimal(- (step_buy_cost * global_buy_commission) / (step_sell_quantity - ((global_sell_profit * total_sell_cost) / (sell_rate * global_sell_commission))))
        if step_buy_rate <= 0.:
            raise error.BuyRateIsLessZero()
        self._parameters[const.PARAMS.STEP_BUY_RATE] = step_buy_rate

    def _ComputeBuyQuantity(self):
        self._parameters[const.PARAMS.STEP_BUY_QUANTITY] = self._QP.Down(self._parameters[const.PARAMS.STEP_BUY_COST] / self._parameters[const.PARAMS.STEP_BUY_RATE])

    def _ComputeSellAndBuyParameters(self):
        # sequence of calculations 1: sell
        self._ComputeSellQuantity()
        self._ComputeSellRate()
        self._ComputeSellCost()
        self._ComputeSellProfit()
        # sequence of calculations 2: buy
        self._ComputeBuyCost()
        self._ComputeBuyRate()
        self._ComputeBuyQuantity()

    @classmethod
    def GetID(cls):
        return const.ID.RCSimple