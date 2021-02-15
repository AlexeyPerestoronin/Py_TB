import math
import copy
import json
import decimal

import common.faf as faf
import common.precision as c_precision

import strategy.const as const
import strategy.const.errors as error
import strategy.stairs.sell_and_buy as ss_sb

# brief: implements simple rate-computed strairs trade-strategy
class SbRcSimple(ss_sb.StairsSellBuy):
    def __init__(self):
        ss_sb.StairsSellBuy.__init__(self)

    def _GetNextBuyRate(self):
        return self._parameters[const.PARAMS.INIT_RATE]

    def _ComputeSellCost(self):
        step_sell_rate = self._parameters[const.PARAMS.STEP_SELL_RATE]
        step_sell_quantity = self._parameters[const.PARAMS.STEP_SELL_QUANTITY]
        self._parameters[const.PARAMS.STEP_SELL_COST] = step_sell_quantity * step_sell_rate

    def _ComputeSellRate(self):
        # Rb
        base_buy_rate = self._GetNextBuyRate()
        # Kp
        profit = self._parameters[const.PARAMS.GLOBAL_PROFIT]
        # Keb
        buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION]
        # Kes
        sell_commission = self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION]
        # Q3
        step_sell_quantity = self._parameters[const.PARAMS.STEP_SELL_QUANTITY]
        # Q1+Q2+Q3
        total_sell_quantity = self._parameters[const.PARAMS.INIT_QUANTITY] + step_sell_quantity
        # C1+C2
        realized_sell_cost = self._parameters[const.PARAMS.STEP_BUY_COST]

        step_sell_rate = (base_buy_rate * (profit * total_sell_quantity - (buy_commission * realized_sell_cost / base_buy_rate))) / (buy_commission * sell_commission * step_sell_quantity)
        # if step_sell_rate <= 0.:
        #     raise error.BuyRateIsLessZero()
        self._parameters[const.PARAMS.STEP_SELL_RATE] = step_sell_rate

    def _ComputeSellQuantity(self):
        ceff_1 = self._parameters[const.PARAMS.STEP_COEFFICIENT_1]
        base_sell_quantity = self._parameters[const.PARAMS.INIT_QUANTITY]
        step_sell_quantity = base_sell_quantity * ceff_1
        self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY] -= step_sell_quantity
        if self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY] < 0.:
            raising_error = error.ExceededAvailableCurrency()
            raising_error.SetBuyQuantity(self._QP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_QUANTITY]))
            raising_error.SetBuyCost(self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_COST]))
            raising_error.SetBuyRate(self._RP.UpDecimal(self._parameters[const.PARAMS.STEP_BUY_RATE]))
            raise raising_error
        self._parameters[const.PARAMS.STEP_SELL_QUANTITY] = step_sell_quantity

    def _ComputeBuyCost(self):
        total_sell_cost = self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL]
        self._parameters[const.PARAMS.STEP_BUY_COST] = total_sell_cost

    def _ComputeBuyProfit(self):
        total_sell_quantity = self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_CLEAN]
        expected_buy_quantity = self._parameters[const.PARAMS.STEP_BUY_QUANTITY]
        self._parameters[const.PARAMS.STEP_BUY_PROFIT] = expected_buy_quantity - total_sell_quantity

    def _ComputeBuyRate(self):
        possible_buy_cost = self._parameters[const.PARAMS.STEP_BUY_COST]
        expected_buy_quantity = self._parameters[const.PARAMS.STEP_BUY_QUANTITY]
        self._parameters[const.PARAMS.STEP_BUY_RATE] = self.ComputeBuyRate(expected_buy_quantity, possible_buy_cost)

    def _ComputeBuyQuantity(self):
        profit = self._parameters[const.PARAMS.GLOBAL_PROFIT]
        total_sell_quantity = self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_CLEAN]
        self._parameters[const.PARAMS.STEP_BUY_QUANTITY] = total_sell_quantity * profit

    def _ComputeSellAndBuyParameters(self):
        # sequence of calculations 1: buy
        self._ComputeBuyQuantity()
        self._ComputeBuyCost()
        self._ComputeBuyRate()
        self._ComputeBuyProfit()
        # sequence of calculations 2: sell
        self._ComputeSellQuantity()
        self._ComputeSellRate()
        self._ComputeSellCost()

    @classmethod
    def GetID(cls):
        return const.ID.SbRcSimple
