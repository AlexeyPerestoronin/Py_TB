import strategy.const as const
import strategy.const.errors as error
import strategy.stairs.buy_and_sell.rate_computed as ss_bs_rc

class BsCcSimple(ss_bs_rc.BsRcSimple):
    def __init__(self):
        ss_bs_rc.BsRcSimple.__init__(self)

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
            raising_error.SetSellQuantity(self._QP.DownDecimal(self._parameters[const.PARAMS.STEP_SELL_QUANTITY]))
            raising_error.SetSellCost(self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_SELL_COST]))
            raising_error.SetSellRate(self._RP.UpDecimal(self._parameters[const.PARAMS.STEP_SELL_RATE]))
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
        step_buy_cost = self._parameters[const.PARAMS.STEP_BUY_COST]
        step_buy_rate = self._parameters[const.PARAMS.STEP_BUY_RATE]
        self._parameters[const.PARAMS.STEP_BUY_QUANTITY] = step_buy_cost / step_buy_rate

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
        return const.ID.BsCcSimple