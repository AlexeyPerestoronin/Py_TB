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
        return self._parameters[const.PARAMS.STEP_INIT_RATE.Key]

    def _ComputeSellCost(self):
        step_sell_rate = self._parameters[const.PARAMS.STEP_SELL_RATE.Key]
        step_sell_quantity = self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key]
        self._parameters[const.PARAMS.STEP_SELL_COST.Key] = step_sell_quantity * step_sell_rate

    def _ComputeSellRate(self):
        base_buy_rate = self._GetNextBuyRate()
        profit = self._parameters[const.PARAMS.GLOBAL_PROFIT.Key]
        buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION.Key]
        sell_commission = self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION.Key]
        step_sell_quantity = self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key]
        total_sell_quantity = self._parameters[const.PARAMS.STEP_INIT_QUANTITY.Key] + step_sell_quantity
        realized_sell_cost = self._parameters[const.PARAMS.STEP_BUY_COST.Key]
        step_sell_rate = (base_buy_rate * (profit * total_sell_quantity - (buy_commission * realized_sell_cost / base_buy_rate))) / (buy_commission * sell_commission * step_sell_quantity)
        self._parameters[const.PARAMS.STEP_SELL_RATE.Key] = step_sell_rate

    def _ComputeSellQuantity(self):
        ceff_1 = self._parameters[const.PARAMS.STEP_COEFFICIENT_1.Key]
        base_sell_quantity = self._parameters[const.PARAMS.STEP_INIT_QUANTITY.Key]
        step_sell_quantity = base_sell_quantity * ceff_1
        self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY.Key] -= step_sell_quantity
        if self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY.Key] < 0.:
            raising_error = error.ExceededAvailableCurrency()
            raising_error.SetBuyQuantity(self._QP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_QUANTITY.Key]))
            raising_error.SetBuyCost(self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_COST.Key]))
            raising_error.SetBuyRate(self._RP.UpDecimal(self._parameters[const.PARAMS.STEP_BUY_RATE.Key]))
            raise raising_error
        self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key] = step_sell_quantity

    def _ComputeBuyCost(self):
        total_sell_cost = self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL]
        self._parameters[const.PARAMS.STEP_BUY_COST.Key] = total_sell_cost

    def _ComputeBuyProfit(self):
        total_sell_quantity = self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_CLEAN]
        expected_buy_quantity = self._parameters[const.PARAMS.STEP_BUY_QUANTITY.Key]
        self._parameters[const.PARAMS.STEP_LEFT_PROFIT.Key] = expected_buy_quantity - total_sell_quantity

    def _ComputeBuyRate(self):
        possible_buy_cost = self._parameters[const.PARAMS.STEP_BUY_COST.Key]
        expected_buy_quantity = self._parameters[const.PARAMS.STEP_BUY_QUANTITY.Key]
        self._parameters[const.PARAMS.STEP_BUY_RATE.Key] = possible_buy_cost / expected_buy_quantity

    def _ComputeBuyQuantity(self):
        profit = self._parameters[const.PARAMS.GLOBAL_PROFIT.Key]
        buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION.Key]
        total_sell_quantity = self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_CLEAN]
        self._parameters[const.PARAMS.STEP_BUY_QUANTITY.Key] = (total_sell_quantity * profit) / buy_commission

    def _ComputeLeftProfit(self):
        buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION.Key]
        total_sell_quantity = self._parameters[const.PARAMS.STEP_INIT_QUANTITY.Key]
        not_commission_buy_quantity = self._parameters[const.PARAMS.STEP_BUY_QUANTITY.Key]
        not_commission_profit = not_commission_buy_quantity - total_sell_quantity
        commission_buy_quantity = not_commission_buy_quantity * buy_commission
        commission_profit = commission_buy_quantity - total_sell_quantity
        full_commission = not_commission_profit - commission_profit
        buy_commission_concession = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION_CONCESSION.Key]
        commission_concession = full_commission * buy_commission_concession
        step_profit_left = commission_profit + commission_concession
        self._parameters[const.PARAMS.STEP_LEFT_PROFIT.Key] = step_profit_left

    def _ComputeRightProfit(self):
        self._parameters[const.PARAMS.STEP_RIGHT_PROFIT.Key] = self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CONCESSION]

    def _ComputeSellAndBuyParameters(self):
        # sequence of calculations 1: buy
        self._ComputeBuyQuantity()
        self._ComputeBuyCost()
        self._ComputeBuyRate()
        # sequence of calculations 2: sell
        self._ComputeSellQuantity()
        self._ComputeSellRate()
        self._ComputeSellCost()
        # sequence of calculations 3: profit
        self._ComputeRightProfit()
        self._ComputeLeftProfit()
    
    def _ReductionPrecisionForSellAndBuyParameters(self):
        # sequence of reduction 1: sell
        self._parameters[const.PARAMS.STEP_SELL_COST.Key] = self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_SELL_COST.Key])
        self._parameters[const.PARAMS.STEP_SELL_RATE.Key] = self._RP.UpDecimal(self._parameters[const.PARAMS.STEP_SELL_RATE.Key])
        self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key] = self._QP.UpDecimal(self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key])
        # sequence of reduction 2: buy
        self._parameters[const.PARAMS.STEP_BUY_COST.Key] = self._CP.UpDecimal(self._parameters[const.PARAMS.STEP_BUY_COST.Key])
        self._parameters[const.PARAMS.STEP_BUY_RATE.Key] = self._RP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_RATE.Key])
        self._parameters[const.PARAMS.STEP_BUY_QUANTITY.Key] = self._QP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_QUANTITY.Key])
        # sequence of reduction 3: profit
        self._parameters[const.PARAMS.STEP_LEFT_PROFIT.Key] = self._QP.DownDecimal(self._parameters[const.PARAMS.STEP_LEFT_PROFIT.Key])
        self._parameters[const.PARAMS.STEP_RIGHT_PROFIT.Key] = self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_RIGHT_PROFIT.Key])

    @classmethod
    def GetID(cls):
        return const.ID.SbRcSimple
