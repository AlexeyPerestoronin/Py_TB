import common.precision as c_precision

import strategy.stairs as ss
import strategy.const as const
import strategy.const.errors as error

# brief: implements template for all simple stairs trade-strategy realizing sell-buy trading principle
class StairsSellBuy(ss.StairsBase):
    def __init__(self):
        ss.StairsBase.__init__(self)

    def _CollectStatistic(self):
        total_sell_rate = None
        total_sell_quantity = None
        sell_commission = self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION]
        if not self._previous_step:
            total_sell_quantity = self._parameters[const.PARAMS.INIT_QUANTITY]
            total_sell_rate = self._parameters[const.PARAMS.INIT_RATE]
        else:
            total_sell_quantity = self._previous_step._parameters[const.PARAMS.STEP_SELL_QUANTITY]
            total_sell_rate = self._previous_step._parameters[const.PARAMS.STEP_SELL_RATE]
        # collection of statistics (volume)
        clean_cost = total_sell_quantity * total_sell_rate
        real_cost = clean_cost * sell_commission
        lost_cost = clean_cost - real_cost
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CLEAN] += clean_cost
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL] += real_cost
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_LOST] += lost_cost
        # collection of statistics (cost)
        self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_CLEAN] += total_sell_quantity
        self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_REAL] += real_cost / total_sell_rate
        self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_LOST] += lost_cost / total_sell_rate

    def _InitializeNextStep(self):
        init_sell_rate = self._parameters[const.PARAMS.INIT_RATE]
        init_sell_quantity = self._parameters[const.PARAMS.INIT_QUANTITY]
        step_sell_rate = self._parameters[const.PARAMS.STEP_SELL_RATE]
        step_sell_quantity = self._parameters[const.PARAMS.STEP_SELL_QUANTITY]
        everage_sell_rate = (init_sell_quantity * init_sell_rate + step_sell_quantity * step_sell_rate) / (init_sell_quantity + step_sell_quantity)
        self._next_step.SetInitRate(everage_sell_rate)
        total_sell_quantity = init_sell_quantity + step_sell_quantity
        self._next_step.SetInitQuantity(total_sell_quantity)
        self._next_step.Init()

    def _InitializeFirstStep(self):
        self._parameters[const.PARAMS.STEP] = 1
        global_currency = self._parameters[const.PARAMS.GLOBAL_AVAILABLE_CURRENCY]
        total_sell_currency = self._parameters[const.PARAMS.INIT_QUANTITY]
        step_available_currency = global_currency - total_sell_currency
        if step_available_currency < 0.:
            raise error.ExceededAvailableCurrency()
        self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY] = step_available_currency

    # NOTE: Get...

    def GetSellCost(self):
        return self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_SELL_COST])

    def GetSellRate(self):
        return self._RP.UpDecimal(self._parameters[const.PARAMS.STEP_SELL_RATE])

    def GetSellQuantity(self):
        return self._QP.DownDecimal(self._parameters[const.PARAMS.STEP_SELL_QUANTITY])

    def GetBuyCost(self):
        return self._CP.UpDecimal(self._parameters[const.PARAMS.STEP_BUY_COST])

    def GetBuyRate(self):
        return self._RP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_RATE])

    def GetBuyQuantity(self):
        return self._QP.UpDecimal(self._parameters[const.PARAMS.STEP_BUY_QUANTITY])

    def GetTotalActivityCost(self):
        return self._CP.UpDecimal(self._parameters[const.PARAMS.INIT_QUANTITY])

    def GetTotalEverageActivityRate(self):
        return self._RP.UpDecimal(self._parameters[const.PARAMS.INIT_RATE])

    def GetStepProfit(self):
        return self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_PROFIT])

    def GetProfit(self):
        return self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_PROFIT])

    def GetDifferenceBetweenRate(self):
        last_sell_rate = None
        step_buy_rate = self._parameters[const.PARAMS.STEP_BUY_RATE]
        if self._previous_step:
            last_sell_rate = self._previous_step._parameters[const.PARAMS.STEP_SELL_RATE]
        else:
            last_sell_rate = self._parameters[const.PARAMS.INIT_RATE]
        difference_between_rate = step_buy_rate - last_sell_rate
        return self._RP.DownDecimal(difference_between_rate)

    @classmethod
    def GetID(cls):
        return const.ID.StairsSellBuy