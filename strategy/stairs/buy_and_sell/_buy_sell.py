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
        buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION.Key]
        buy_commission_concession = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION_CONCESSION.Key]
        if not self._previous_step:
            total_buy_cost = self._parameters[const.PARAMS.STEP_INIT_COST.Key]
            total_buy_rate = self._parameters[const.PARAMS.STEP_INIT_RATE.Key]
        else:
            total_buy_cost = self._previous_step._parameters[const.PARAMS.STEP_BUY_COST.Key]
            total_buy_rate = self._previous_step._parameters[const.PARAMS.STEP_BUY_RATE.Key]
        # collection of statistics (volume)
        clean_quantity = total_buy_cost / total_buy_rate
        real_quantity = clean_quantity * buy_commission
        lost_quantity = clean_quantity - real_quantity
        total_concession_quantity = lost_quantity * buy_commission_concession
        self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_CLEAN] += clean_quantity
        self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_REAL] += real_quantity
        self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_LOST] += lost_quantity
        self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_CONCESSION] += total_concession_quantity
        # collection of statistics (cost)
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CLEAN] += total_buy_cost
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL] += real_quantity * total_buy_rate
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_LOST] += lost_quantity * total_buy_rate

    def _InitializeNextStep(self):
        next_sell_rate = self._GetNextSellRate()
        buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION.Key]
        profit = self._parameters[const.PARAMS.GLOBAL_PROFIT.Key]
        everage_buy_rate = buy_commission**2 * next_sell_rate / profit
        self._next_step.SetInitRate(everage_buy_rate)
        total_buy_cost = self._parameters[const.PARAMS.STEP_INIT_COST.Key] + self._parameters[const.PARAMS.STEP_BUY_COST.Key]
        self._next_step.SetInitCost(total_buy_cost)
        self._next_step.Init()

    def _InitializeFirstStep(self):
        self._parameters[const.PARAMS.STEP_NUMBER.Key] = 1
        global_currency = self._parameters[const.PARAMS.GLOBAL_AVAILABLE_CURRENCY.Key]
        total_buy_currency = self._parameters[const.PARAMS.STEP_INIT_COST.Key]
        step_available_currency = global_currency - total_buy_currency
        if step_available_currency < 0.:
            raise error.ExceededAvailableCurrency()
        self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY.Key] = step_available_currency

    # NOTE: Get...

    def GetDifferenceBetweenRate(self):
        last_buy_rate = None
        step_sell_rate = self._parameters[const.PARAMS.STEP_SELL_RATE.Key]
        if self._previous_step:
            last_buy_rate = self._previous_step._parameters[const.PARAMS.STEP_BUY_RATE.Key]
        else:
            last_buy_rate = self._parameters[const.PARAMS.STEP_INIT_RATE.Key]
        difference_between_rate = step_sell_rate - last_buy_rate
        return self._RP.DownDecimal(difference_between_rate)

    @classmethod
    def GetID(cls):
        return const.ID.StairsBuySell
