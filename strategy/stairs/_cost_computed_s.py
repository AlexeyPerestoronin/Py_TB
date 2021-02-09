import strategy.stairs as ss
import strategy.const as const
import strategy.const.errors as error

class CostComputedS(ss.Simple):
    def __init__(self):
        ss.Simple.__init__(self)

    # brief: compute buy-cost for current strategy-step to buy-action
    def _ComputeBuyCost(self):
        sell_rate = self._GetNextSellRate()
        sell_profit = self._parameters[const.PARAMS.GLOBAL_PROFIT]
        sell_total_cost = self._parameters[const.PARAMS.INIT_COST]
        sell_commission = self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION]
        sell_total_quantity = self._parameters[const.PARAMS.STEP_SELL_QUANTITY]
        buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION]
        buy_rate = self._parameters[const.PARAMS.STEP_BUY_RATE]
        buy_cost = - ((sell_profit * sell_total_cost) - (sell_commission * sell_rate * sell_total_quantity)) / (sell_profit - (buy_commission**2 * sell_rate / buy_rate))
        if buy_cost < 0.:
            raise error.BuyCostIsLessZero()
        self._parameters[const.PARAMS.STEP_BUY_COST] = buy_cost
        self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY] -= buy_cost
        if self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY] < 0.:
            raising_error = error.ExceededAvailableCurrency()
            raising_error.SetSellQuantity(self._parameters[const.PARAMS.STEP_SELL_QUANTITY])
            raising_error.SetSellCost(self._parameters[const.PARAMS.STEP_SELL_COST])
            raising_error.SetSellRate(self._parameters[const.PARAMS.STEP_SELL_RATE])
            raise raising_error

    # brief: compute buy-rate for current strategy-step to buy-action
    def _ComputeBuyRate(self):
        if self._previous_step:
            self._parameters[const.PARAMS.STEP_BUY_RATE] = self._previous_step._parameters[const.PARAMS.STEP_BUY_RATE] - self._parameters[const.PARAMS.STEP_COEFFICIENT_1]
        else:
            self._parameters[const.PARAMS.STEP_BUY_RATE] = self._parameters[const.PARAMS.INIT_RATE] - self._parameters[const.PARAMS.STEP_COEFFICIENT_1]
        if self._parameters[const.PARAMS.STEP_BUY_RATE] <= 0.:
            raise error.BuyRateIsLessZero()

    # brief: compute buy-quantity for current strategy-step to buy-action
    def _ComputeBuyQuantity(self):
        self._parameters[const.PARAMS.STEP_BUY_QUANTITY] = self._QP.Down(self._parameters[const.PARAMS.STEP_BUY_COST] / self._parameters[const.PARAMS.STEP_BUY_RATE])

    # brief: compute current strategy-step
    def _ComputeCurrentStep(self):
        self._CollectStatistic()
        # (ceff) sequence of calculations
        self._ComputeNextCoefficient1()
        # (sell) sequence of calculations
        self._ComputeSellQuantity()
        self._ComputeSellRate()
        self._ComputeSellCost()
        self._ComputeSellProfit()
        # (buy) sequence of calculations
        self._ComputeBuyRate()
        self._ComputeBuyCost()
        self._ComputeBuyQuantity()

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.COST_COMPUTED_S