import math
import copy
import json
import decimal

import common.faf as faf
import common.precision as c_precision

import strategy.const as const
import strategy.const.errors as error
import strategy.stairs.buy_and_sell as ss_bs

# brief: implements simple rate-computed strairs trade-strategy
class BsRcSimple(ss_bs.StairsBuySell):
    def __init__(self):
        ss_bs.StairsBuySell.__init__(self)

    def _GetNextSellRate(self):
        return self._parameters[const.PARAMS.STEP_INIT_RATE.Key]

    def _ComputeSellCost(self):
        sell_rate = self._parameters[const.PARAMS.STEP_SELL_RATE.Key]
        total_buy_quantity = self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key]
        self._parameters[const.PARAMS.STEP_SELL_COST.Key] = total_buy_quantity * sell_rate

    def _ComputeSellRate(self):
        profit = self._parameters[const.PARAMS.GLOBAL_PROFIT.Key]
        total_buy_cost = self._parameters[const.PARAMS.STEP_INIT_COST.Key]
        total_buy_quantity = self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key]
        self._parameters[const.PARAMS.STEP_SELL_RATE.Key] = self.ComputeSellRate(total_buy_quantity, total_buy_cost * profit)

    def _ComputeSellQuantity(self):
        total_buy_quantity = self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_REAL]
        self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key] = total_buy_quantity

    def _ComputeBuyCost(self):
        total_buy_cost = self._parameters[const.PARAMS.STEP_INIT_COST.Key]
        ceff_1 = self._parameters[const.PARAMS.STEP_COEFFICIENT_1.Key]
        self._parameters[const.PARAMS.STEP_BUY_COST.Key] = total_buy_cost * ceff_1

    def _ComputeBuyRate(self):
        base_sell_rate = self._GetNextSellRate()
        self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY.Key] -= self._parameters[const.PARAMS.STEP_BUY_COST.Key]
        if self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY.Key] < 0.:
            raising_error = error.ExceededAvailableCurrency()
            raising_error.SetSellQuantity(self._QP.DownDecimal(self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key]))
            raising_error.SetSellCost(self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_SELL_COST.Key]))
            raising_error.SetSellRate(self._RP.UpDecimal(self._parameters[const.PARAMS.STEP_SELL_RATE.Key]))
            raise raising_error
        profit = self._parameters[const.PARAMS.GLOBAL_PROFIT.Key]
        buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION.Key]
        sell_commission = self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION.Key]
        total_sell_cost = self._parameters[const.PARAMS.STEP_INIT_COST.Key] + self._parameters[const.PARAMS.STEP_BUY_COST.Key]
        step_sell_quantity = self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key]
        step_buy_cost = self._parameters[const.PARAMS.STEP_BUY_COST.Key]
        step_buy_rate = - (step_buy_cost * buy_commission) / (step_sell_quantity - ((profit * total_sell_cost) / (base_sell_rate * sell_commission)))
        if self._RP.DownDecimal(step_buy_rate) <= 0.:
            raise error.BuyRateIsLessZero()
        self._parameters[const.PARAMS.STEP_BUY_RATE.Key] = step_buy_rate

    def _ComputeBuyQuantity(self):
        step_buy_cost = self._parameters[const.PARAMS.STEP_BUY_COST.Key]
        step_buy_rate = self._parameters[const.PARAMS.STEP_BUY_RATE.Key]
        self._parameters[const.PARAMS.STEP_BUY_QUANTITY.Key] = step_buy_cost / step_buy_rate

    def _ComputeLeftProfit(self):
        self._parameters[const.PARAMS.STEP_LEFT_PROFIT.Key] = self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_CONCESSION]

    def _ComputeRightProfit(self):
        sell_commission = self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION.Key]
        total_buy_cost = self._parameters[const.PARAMS.STEP_INIT_COST.Key]
        sell_cost = self._parameters[const.PARAMS.STEP_SELL_COST.Key]
        not_commission_profit = sell_cost - total_buy_cost
        commission_profit = (sell_cost * sell_commission) - total_buy_cost
        full_commission = not_commission_profit - commission_profit
        sell_commission_concession = self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION_CONCESSION.Key]
        commission_concession = full_commission * sell_commission_concession
        step_profit_right = commission_profit + commission_concession
        self._parameters[const.PARAMS.STEP_RIGHT_PROFIT.Key] = step_profit_right

    def _ComputeSellAndBuyParameters(self):
        # sequence of calculations 1: sell
        self._ComputeSellQuantity()
        self._ComputeSellRate()
        self._ComputeSellCost()
        # sequence of calculations 2: buy
        self._ComputeBuyCost()
        self._ComputeBuyRate()
        self._ComputeBuyQuantity()
        # sequence of calculations 3: profit
        self._ComputeLeftProfit()
        self._ComputeRightProfit()

    def _ReductionPrecisionForSellAndBuyParameters(self):
        # sequence of reduction 1: sell
        self._parameters[const.PARAMS.STEP_SELL_COST.Key] = self._CP.UpDecimal(self._parameters[const.PARAMS.STEP_SELL_COST.Key])
        self._parameters[const.PARAMS.STEP_SELL_RATE.Key] = self._RP.UpDecimal(self._parameters[const.PARAMS.STEP_SELL_RATE.Key])
        self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key] = self._QP.DownDecimal(self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key])
        # sequence of reduction 2: buy
        self._parameters[const.PARAMS.STEP_BUY_COST.Key] = self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_COST.Key])
        self._parameters[const.PARAMS.STEP_BUY_RATE.Key] = self._RP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_RATE.Key])
        self._parameters[const.PARAMS.STEP_BUY_QUANTITY.Key] = self._QP.UpDecimal(self._parameters[const.PARAMS.STEP_BUY_QUANTITY.Key])
        # sequence of reduction 3: profit
        self._parameters[const.PARAMS.STEP_LEFT_PROFIT.Key] = self._QP.DownDecimal(self._parameters[const.PARAMS.STEP_LEFT_PROFIT.Key])
        self._parameters[const.PARAMS.STEP_RIGHT_PROFIT.Key] = self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_RIGHT_PROFIT.Key])

    @classmethod
    def GetID(cls):
        return const.ID.BsRcSimple
