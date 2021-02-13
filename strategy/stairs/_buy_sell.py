import common.precision as c_precision

import strategy.stairs as ss
import strategy.const as const
import strategy.const.errors as error

# brief: implements template for all simple stairs trade-strategy realizing buy-sell trading principle
class StairsBuySell(ss.StairsBase):
    def __init__(self):
        ss.StairsBase.__init__(self)

    def _CollectStatistic(self):
        total_buy_cost = None
        total_buy_rate = None
        buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION]
        if not self._previous_step:
            total_buy_cost = self._parameters[const.PARAMS.INIT_COST]
            total_buy_rate = self._parameters[const.PARAMS.INIT_RATE]
        else:
            total_buy_cost = self._previous_step._parameters[const.PARAMS.STEP_BUY_COST]
            total_buy_rate = self._previous_step._parameters[const.PARAMS.STEP_BUY_RATE]
        # collection of statistics (volume)
        clean_quantity = total_buy_cost / total_buy_rate
        real_quantity = clean_quantity * buy_commission
        lost_quantity = clean_quantity - real_quantity
        self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_CLEAN] += clean_quantity
        self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_REAL] += real_quantity
        self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_LOST] += lost_quantity
        # collection of statistics (cost)
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CLEAN] += total_buy_cost
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL] += real_quantity * total_buy_rate
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_LOST] += lost_quantity * total_buy_rate

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
        return self._CP.UpDecimal(self._parameters[const.PARAMS.INIT_COST])

    def GetTotalEverageActivityRate(self):
        return self._RP.UpDecimal(self._parameters[const.PARAMS.INIT_RATE])

    def GetStepProfit(self):
        return self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_SELL_PROFIT])

    def GetProfit(self):
        return self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_SELL_PROFIT])

    def GetDifferenceBetweenRate(self):
        difference_between_rate = None
        if self._previous_step:
            difference_between_rate = self._parameters[const.PARAMS.STEP_SELL_RATE] - self._previous_step._parameters[const.PARAMS.STEP_BUY_RATE]
        else:
            difference_between_rate = self._parameters[const.PARAMS.STEP_SELL_RATE] - self._parameters[const.PARAMS.INIT_RATE]
        return self._RP.DownDecimal(difference_between_rate)

    @classmethod
    def GetID(cls):
        return const.ID.StairsBuySell
