import math
import copy

import strategy
import strategy.const as const

class StairsSimple:
    def __init__(self):
        self._step = None
        self._coefficient = None
        self._commission = None
        self._profit = None
        self._init_rate = None
        self._init_cost = None
        self._sell_rate = None
        self._buy_rate = None
        self._buy_cost = None
        self._next_step = None
        self._previous_step = None
        self._statistic = {
            const.INFO.GLOBAL.VOLUME : {
                const.INFO.GLOBAL.VOLUME.TOTAL_CLEAN : 0,
                const.INFO.GLOBAL.VOLUME.TOTAL_REAL : 0,
                const.INFO.GLOBAL.VOLUME.TOTAL_LOST : 0,
            },
            const.INFO.GLOBAL.COST : {
                const.INFO.GLOBAL.COST.TOTAL_CLEAN : 0,
                const.INFO.GLOBAL.COST.TOTAL_REAL : 0,
                const.INFO.GLOBAL.COST.TOTAL_LOST : 0,
            }
        }

    # collects statistic for all steps of trade-strategy
    def _CollectStatistic(self):
        if not self._previous_step:
            clean_volume = self._init_cost / self._init_rate
            real_volume = clean_volume * self._commission
            lost_volume = clean_volume - real_volume
            # collection of statistics (volume)
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_CLEAN] = clean_volume
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_REAL] = real_volume
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_LOST] = lost_volume
            # collection of statistics (cost)
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CLEAN] = self._init_cost
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL] = real_volume * self._init_rate
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_LOST] = lost_volume * self._init_rate
        else:
            # collection of statistics (volume)
            clean_volume = self._previous_step._buy_cost / self._previous_step._buy_rate
            real_volume = clean_volume * self._previous_step._commission
            lost_volume = clean_volume - real_volume
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_CLEAN] += clean_volume
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_REAL] += real_volume
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_LOST] += lost_volume
            # collection of statistics (cost)
            clean_cost = self._previous_step._buy_cost
            real_cost = real_volume * self._previous_step._buy_rate
            lost_cost = clean_cost - real_cost
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CLEAN] += clean_cost
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL] += real_cost
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_LOST] += lost_cost

    # brief: compute rate of strategy-trade for current strategy-step to sell-action
    # return: trade-rate for sell
    def _ComputeSellRate(self):
        self._sell_rate = self.ComputeSellRateForProfit(self._profit)

    # brief: compute buy-rate of strategy-trade for current strategy-step to buy-action
    # return: computed buy-rate
    def _ComputeBuyRate(self):
        sell_rate = self.GetNextSellRate()
        self._buy_cost = self.GetNextBuyCost()
        volume = self._init_cost / self._init_rate * self._commission
        sell_cost = self._init_cost + self._buy_cost
        self._buy_rate = - (self._buy_cost * self._commission) / (volume - ((self._profit * sell_cost) / (sell_rate * self._commission)))

    # brief: set the coefficient of each next cost increaseble
    # param: coefficient - new each next cost increaseble
    def SetCoefficient(self, coefficient):
        self._coefficient = coefficient

    # brief: set a trade-commission
    # param: commission - new value of a trade-commission
    def SetCommission(self, commission):
        self._commission = commission

    # brief: set a trade-profit
    # param: profit - new value of a trade-profit
    def SetProfit(self, profit):
        self._profit = profit

    # brief: strategy initialization
    # note1: this function must be called only after call of SetCoefficient, SetCommission and SetProfit functions
    # param: rate - currency rate on first-step
    # param: cost - currency cost on first-step
    def Init(self, rate, cost):
        self._step = 1
        if self._previous_step:
            self._step = self._previous_step._step + 1
            self._statistic = copy.deepcopy(self._previous_step._statistic)
        self._init_rate = rate
        self._init_cost = cost
        self._ComputeSellRate()
        self._ComputeBuyRate()
        self._CollectStatistic()

    # brief: gets sell-rate for current-step
    # return: the sell-rate for current-step
    def GetSellRate(self):
        return self._sell_rate

    # brief: gets sell-rate for next-step
    # return: the sell-rate for next-step
    def GetNextSellRate(self):
        return self._init_rate

    # brief: gets buy-rate for current-step
    # return: the buy-rate for current-step
    def GetBuyRate(self):
        return self._buy_rate

    # brief: gets buy-cost for next step
    # return: the buy-cost for next-step
    def GetNextBuyCost(self):
        return self._init_cost * self._coefficient

    # brief: compute sell-rate of strategy-trade for current strategy-step for desired profit
    # param: desired_profit - desired profit from sell
    # return: trade-rate for sell
    def ComputeSellRateForProfit(self, desired_profit):
        real_volume = self._init_cost / self._init_rate * self._commission
        return (self._init_cost * desired_profit) / (self._commission * real_volume)

    # brief: compute next trade-step based of current trade-step
    # return: next trade-step
    def ComputeNextStep(self):
        self._next_step = type(self)()
        self._next_step.SetProfit(self._profit)
        self._next_step.SetCommission(self._commission)
        self._next_step.SetCoefficient(self._coefficient)
        cost = self._init_cost + self._buy_cost
        rate = (math.pow(self._commission, 2) * self.GetNextSellRate()) / self._profit
        self._next_step._previous_step = self
        self._next_step.Init(rate, cost)
        return self._next_step

    def GetDifferenceBetweenRate(self):
        difference_between_rate = None
        if self._previous_step:
            difference_between_rate = self._sell_rate - self._previous_step._buy_rate
        else:
            difference_between_rate = self._sell_rate - self._init_rate
        return difference_between_rate

    # param: getted full information about current step of the trading-strategy
    # return: full information about trading-strategy
    def GetInfo(self):
        info = {
            const.INFO.GLOBAL : {
                const.INFO.GLOBAL.COMMISSION : {
                    const.INFO.VALUE : self._commission,
                    const.INFO.DESCRIPTION : "commission for buy/sale transactions imposed by the trading-exchange"
                },
                const.INFO.GLOBAL.PROFIT : {
                    const.INFO.VALUE : self._profit,
                    const.INFO.DESCRIPTION : "profit realized by the trading-strategy"
                },
                const.INFO.GLOBAL.COEFFICIENT : {
                    const.INFO.VALUE : self._coefficient,
                    const.INFO.DESCRIPTION : "increase-cost-coefficient for each next step of the trading-strategy"
                },
                const.INFO.GLOBAL.VOLUME : {
                    const.INFO.GLOBAL.VOLUME.TOTAL_CLEAN : {
                        const.INFO.VALUE : self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_CLEAN],
                        const.INFO.DESCRIPTION : "total-clean(without commission)-bought-volume of currency at the beggining of the current step"
                    },
                    const.INFO.GLOBAL.VOLUME.TOTAL_REAL : {
                        const.INFO.VALUE : self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_REAL],
                        const.INFO.DESCRIPTION : "total-real(with commission)-bought-volume of currency at the beggining of the current step"
                    },
                    const.INFO.GLOBAL.VOLUME.TOTAL_LOST : {
                        const.INFO.VALUE : self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_LOST],
                        const.INFO.DESCRIPTION : "total-lost(by commission)-volume of currency at the beggining of the current step"
                    },
                },
                const.INFO.GLOBAL.COST : {
                    const.INFO.GLOBAL.COST.TOTAL_CLEAN : {
                        "value" : self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CLEAN],
                        "description" : "total curency cost at the current trading-strategy step"
                    },
                    const.INFO.GLOBAL.COST.TOTAL_REAL : {
                        "value" : self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL],
                        "description" : "real curency cost at the current trading-strategy step"
                    },
                    const.INFO.GLOBAL.COST.TOTAL_LOST : {
                        "value" : self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_LOST],
                        "description" : "losted cost at the current trading-strategy step"
                    },
                },
            },
            const.INFO.STEP : {
                const.INFO.STEP.DIFFERENCE_RATE : {
                    const.INFO.VALUE : self.GetDifferenceBetweenRate(),
                    const.INFO.DESCRIPTION : "the difference between last buy-rate and current sell-rate"
                },
                const.INFO.STEP.AVERAGE_PRICE : {
                    const.INFO.VALUE : self._init_rate,
                    const.INFO.DESCRIPTION : "total-everage-price is buy-rate of currency on total-cost at the in current step"
                },
                const.INFO.STEP.TOTAL_BUY_COST : {
                    const.INFO.VALUE : self._init_cost,
                    const.INFO.DESCRIPTION : "total-buy-cost of currency in current step"
                },
                const.INFO.STEP.SELL_RATE : {
                    const.INFO.VALUE : self._sell_rate,
                    const.INFO.DESCRIPTION : "currency-sell-rate need for realized actual profit of the trading-strategy"
                },
                const.INFO.STEP.SELL_RATE_0 : {
                    const.INFO.VALUE : self.ComputeSellRateForProfit(1.0),
                    const.INFO.DESCRIPTION : "currency-sell-rate need for realized 0%-profit of the trading-strategy"
                },
                const.INFO.STEP.NEXT_BUY_RATE : {
                    const.INFO.VALUE : self._buy_rate,
                    const.INFO.DESCRIPTION : "maximum currency buy-rate need for going to next step of the current trading-strategy"
                },
                const.INFO.STEP.NEXT_BUY_COST : {
                    const.INFO.VALUE : self._buy_cost,
                    const.INFO.DESCRIPTION : "cost of curency for next buy-step of the current trading-strategy"
                },
            },
        }
        return info

    # brief: gets current trade-strategy step
    # return: current trade-strategy step
    def GetStep(self):
        return self._step

    # brief: get strategy-ID
    # return: strategy-ID
    @staticmethod
    def GetID():
        return const.ID.STAIRS_SIMPLE
