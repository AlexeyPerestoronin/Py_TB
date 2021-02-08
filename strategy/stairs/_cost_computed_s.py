import strategy.stairs as ss
import strategy.const as const
import strategy.const.errors as error

class CostComputedS(ss.Simple):
    def __init__(self):
        ss.Simple.__init__(self)
        self._rate_decrease = None

    # brief: compute buy-cost for current strategy-step to buy-action
    def _ComputeBuyCost(self):
        sell_rate = self._GetNextSellRate()
        self._buy_cost = - ((self._profit * self._init_cost) - (self._sell_commission * sell_rate * self._sell_quantity)) / (self._profit - (self._buy_commission**2 * sell_rate / self._buy_rate))
        self._current_available_currency -= self._buy_cost
        if self._current_available_currency < 0.:
            raising_error = error.ExceededAvailableCurrency()
            raising_error.SetSellQuantity(self._sell_quantity)
            raising_error.SetSellCost(self._sell_cost)
            raising_error.SetSellRate(self._sell_rate)
            raise raising_error

    # brief: compute buy-rate for current strategy-step to buy-action
    def _ComputeBuyRate(self):
        if self._previous_step:
            self._buy_rate = self._previous_step._buy_rate - self._rate_decrease
        else:
            self._buy_rate = self._init_rate - self._rate_decrease
        if self._buy_rate <= 0.:
            raise error.BuyRateIsLessZero()

    # brief: compute buy-quantity for current strategy-step to buy-action
    def _ComputeBuyQuantity(self):
        self._buy_quantity = self._QPD(self._buy_cost / self._buy_rate)

    # brief: compute current strategy-step
    def _ComputeCurrentStep(self):
        self._CollectStatistic()
        # (ceff) sequence of calculations
        self._ComputeNextCoefficient()
        # (sell) sequence of calculations
        self._ComputeSellQuantity()
        self._ComputeSellRate()
        self._ComputeSellCost()
        self._ComputeSellProfit()
        # (buy) sequence of calculations
        self._ComputeBuyRate()
        self._ComputeBuyCost()
        self._ComputeBuyQuantity()

    def _MigrateSettings(self):
        ss.Simple._MigrateSettings(self)
        self._next_step.SetRateDecrease(self._rate_decrease)

    def SetRateDecrease(self, rate_decrease):
        self._rate_decrease = rate_decrease

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.COST_COMPUTED_S