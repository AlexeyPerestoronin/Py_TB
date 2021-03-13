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
        sell_commission = self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION.Key]
        sell_commission_concession = self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION_CONCESSION.Key]
        if not self._previous_step:
            total_sell_quantity = self._parameters[const.PARAMS.STEP_INIT_QUANTITY.Key]
            total_sell_rate = self._parameters[const.PARAMS.STEP_INIT_RATE.Key]
        else:
            total_sell_quantity = self._previous_step._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key]
            total_sell_rate = self._previous_step._parameters[const.PARAMS.STEP_SELL_RATE.Key]
        # collection of statistics (volume)
        clean_cost = total_sell_quantity * total_sell_rate
        real_cost = clean_cost * sell_commission
        lost_cost = clean_cost - real_cost
        total_concession_cost = lost_cost * sell_commission_concession
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CLEAN] += clean_cost
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL] += real_cost
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_LOST] += lost_cost
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CONCESSION] += total_concession_cost
        # collection of statistics (cost)
        self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_CLEAN] += total_sell_quantity
        self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_REAL] += real_cost / total_sell_rate
        self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_LOST] += lost_cost / total_sell_rate

    def _InitializeNextStep(self):
        init_sell_rate = self._parameters[const.PARAMS.STEP_INIT_RATE.Key]
        init_sell_quantity = self._parameters[const.PARAMS.STEP_INIT_QUANTITY.Key]
        step_sell_rate = self._parameters[const.PARAMS.STEP_SELL_RATE.Key]
        step_sell_quantity = self._parameters[const.PARAMS.STEP_SELL_QUANTITY.Key]
        everage_sell_rate = (init_sell_quantity * init_sell_rate + step_sell_quantity * step_sell_rate) / (init_sell_quantity + step_sell_quantity)
        self._next_step.SetInitRate(everage_sell_rate)
        total_sell_quantity = init_sell_quantity + step_sell_quantity
        self._next_step.SetInitQuantity(total_sell_quantity)
        self._next_step.Init()

    def _InitializeFirstStep(self):
        self._parameters[const.PARAMS.STEP_NUMBER.Key] = 1
        global_currency = self._parameters[const.PARAMS.GLOBAL_AVAILABLE_CURRENCY.Key]
        total_sell_currency = self._parameters[const.PARAMS.STEP_INIT_QUANTITY.Key]
        step_available_currency = global_currency - total_sell_currency
        if step_available_currency < 0.:
            raise error.ExceededAvailableCurrency()
        self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY.Key] = step_available_currency

    # NOTE: Get...

    def GetDifferenceBetweenRate(self):
        last_sell_rate = None
        step_buy_rate = self._parameters[const.PARAMS.STEP_BUY_RATE.Key]
        if self._previous_step:
            last_sell_rate = self._previous_step._parameters[const.PARAMS.STEP_SELL_RATE.Key]
        else:
            last_sell_rate = self._parameters[const.PARAMS.STEP_INIT_RATE.Key]
        difference_between_rate = step_buy_rate - last_sell_rate
        return self._RP.DownDecimal(difference_between_rate)

    @classmethod
    def GetID(cls):
        return const.ID.StairsSellBuy
