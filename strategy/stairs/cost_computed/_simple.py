import strategy.const as const
import strategy.const.errors as error
import strategy.stairs.rate_computed as ss_rc

class CCSimple(ss_rc.RCSimple):
    def __init__(self):
        ss_rc.RCSimple.__init__(self)

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

    def _ComputeBuyRate(self):
        base_rate = None
        coefficient1 = self._parameters[const.PARAMS.STEP_COEFFICIENT_1]
        if self._previous_step:
            base_rate = self._previous_step._parameters[const.PARAMS.STEP_BUY_RATE]
        else:
            base_rate = self._parameters[const.PARAMS.INIT_RATE]
        buy_rate = base_rate - coefficient1
        if buy_rate <= 0.:
            raise error.BuyRateIsLessZero()
        self._parameters[const.PARAMS.STEP_BUY_RATE] = buy_rate

    def _ComputeBuyQuantity(self):
        self._parameters[const.PARAMS.STEP_BUY_QUANTITY] = self._QP.Down(self._parameters[const.PARAMS.STEP_BUY_COST] / self._parameters[const.PARAMS.STEP_BUY_RATE])

    def _ComputeSellAndBuyParameters(self):
        # sequence of calculations 1: sell
        self._ComputeSellQuantity()
        self._ComputeSellRate()
        self._ComputeSellCost()
        self._ComputeSellProfit()
        # sequence of calculations 2: buy
        self._ComputeBuyRate()
        self._ComputeBuyCost()
        self._ComputeBuyQuantity()

    @classmethod
    def GetID(cls):
        return const.ID.CCSimple