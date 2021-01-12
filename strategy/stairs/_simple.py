import math
import copy
import json
import decimal

import strategy
import common.faf as faf
import strategy.const as const

_d = decimal.Decimal

# brief: implements simple strairs trade-strategy
class Simple:
    def __init__(self):
        self._step = None
        self._price_precision = None
        self._volume_precision = None
        self._coefficient = None
        self._commission = None
        self._profit = None
        self._init_rate = None
        self._init_cost = None
        self._sell_rate = None
        self._sell_quantity = None
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

    # brief: round-up the number to predefined precision
    # param: number - target number for round
    # return: rounded number
    def _RoundUp(self, number):
        return float(_d(number).quantize(self._price_precision, decimal.ROUND_CEILING))

    # brief: round-down the number to predefined precision
    # param: number - target number for round
    # return: rounded number
    def _RoundDown(self, number):
        return float(_d(number).quantize(self._price_precision, decimal.ROUND_FLOOR))

    # collects statistic for all steps of trade-strategy
    def _CollectStatistic(self):
        if not self._previous_step:
            clean_quantity = self._init_cost / self._init_rate
            real_quantity = clean_quantity * self._commission
            real_quantity = float(_d(real_quantity).quantize(self._volume_precision, decimal.ROUND_FLOOR))
            lost_quantity = clean_quantity - real_quantity
            # collection of statistics (volume)
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_CLEAN] = clean_quantity
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_REAL] = real_quantity
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_LOST] = lost_quantity
            # collection of statistics (cost)
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CLEAN] = self._init_cost
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL] = real_quantity * self._init_rate
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_LOST] = lost_quantity * self._init_rate
        else:
            # collection of statistics (volume)
            clean_quantity = self._previous_step._buy_cost / self._previous_step._buy_rate
            real_quantity = clean_quantity * self._previous_step._commission
            real_quantity = float(_d(real_quantity).quantize(self._volume_precision, decimal.ROUND_FLOOR))
            lost_quantity = clean_quantity - real_quantity
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_CLEAN] += clean_quantity
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_REAL] += real_quantity
            self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_LOST] += lost_quantity
            # collection of statistics (cost)
            clean_cost = self._previous_step._buy_cost
            real_cost = real_quantity * self._previous_step._buy_rate
            lost_cost = clean_cost - real_cost
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CLEAN] += clean_cost
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL] += real_cost
            self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_LOST] += lost_cost

    # brief: gets sell-rate for next-step
    # return: the sell-rate for next-step
    def _GetNextSellRate(self):
        return self._init_rate

    # brief: compute rate of strategy-trade for current strategy-step to sell-action
    # return: trade-rate for sell
    def _ComputeSellRate(self):
        self._sell_quantity = self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_REAL]
        self._sell_rate = self.ComputeSellRate(self._sell_quantity, self._init_cost * self._profit)

    # brief: compute buy-rate of strategy-trade for current strategy-step to buy-action
    # return: computed buy-rate
    def _ComputeBuyRate(self):
        sell_rate = self._GetNextSellRate()
        self._buy_cost = self.GetBuyCost()
        sell_cost = self._init_cost + self._buy_cost
        self._buy_rate = self._RoundDown(- (self._buy_cost * self._commission) / (self._sell_quantity - ((self._profit * sell_cost) / (sell_rate * self._commission))))

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

    # brief: set a precision of all mathematical operations performs with volume of currency
    # param: precision - new value of a precision (must be positive integer number)
    def SetVolumePrecision1(self, precision):
        self._volume_precision = "1."
        for _ in range(precision):
            self._volume_precision+="0"
        self._volume_precision = _d(self._volume_precision)

    # brief: set a precision of all mathematical operations performs with volume of currency
    # param: precision - new value of a precision
    def SetVolumePrecision2(self, precision):
        self._volume_precision = _d(precision)

    # brief: set a precision of all mathematical operations performs with trade-rate
    # param: precision - new value of a precision (must be positive integer number)
    def SetPricePrecision1(self, precision):
        self._price_precision = "1."
        for _ in range(precision):
            self._price_precision+="0"
        self._price_precision = _d(self._price_precision)

    # brief: set a precision of all mathematical operations performs with trade-rate
    # param: precision - new value of a precision
    def SetPricePrecision2(self, precision):
        self._price_precision = _d(precision)

    # brief: strategy initialization
    # note1: this function must be called only after call of SetCoefficient, SetCommission and SetProfit functions
    # param: rate - currency rate on first-step
    # param: cost - currency cost on first-step
    def Init(self, rate, cost):
        self._step = 1
        if self._previous_step:
            self._step = self._previous_step._step + 1
            self._statistic = copy.deepcopy(self._previous_step._statistic)
        self._init_rate = self._RoundUp(rate)
        self._init_cost = cost
        self._CollectStatistic()
        self._ComputeSellRate()
        self._ComputeBuyRate()

    # brief: gets sell-rate for current step
    # return: the sell-rate for current step
    def GetSellRate(self):
        return self._sell_rate

    # brief: gets quantity for sell-order for current step
    # return: the quantity for sell-order for current step
    def GetSellQuantity(self):
        return self._sell_quantity

    # brief: gets buy-rate for current step
    # return: the buy-rate for current step
    def GetBuyRate(self):
        return self._buy_rate

    # brief: gets buy-cost for current step
    # return: the buy-cost for current step
    def GetBuyCost(self):
        return self._init_cost * self._coefficient

    # brief: gets buy-quantity for current step
    # return: the buy-quantity for current step
    def GetBuyQuantity(self):
        return self.GetBuyCost() / self.GetBuyRate()

    # brief: compute next trade-step based of current trade-step
    # return: next trade-step
    def ComputeNextStep(self):
        self._next_step = type(self)()
        self._next_step.SetProfit(self._profit)
        self._next_step.SetPricePrecision2(self._price_precision)
        self._next_step.SetVolumePrecision2(self._volume_precision)
        self._next_step.SetCommission(self._commission)
        self._next_step.SetCoefficient(self._coefficient)
        cost = self._init_cost + self._buy_cost
        rate = (math.pow(self._commission, 2) * self._GetNextSellRate()) / self._profit
        self._next_step._previous_step = self
        self._next_step.Init(rate, cost)
        return self._next_step

    # brief: goes to the target-step in current trade-strategy
    # param: step - target trade-step
    # return: the trade strategy in target trade-step state
    def ComputeToStep(self, step):
        copy_strategy = copy.deepcopy(self)
        while step != copy_strategy._step:
            if copy_strategy._step < step:
                copy_strategy = copy_strategy.ComputeNextStep()
            else:
                copy_strategy = copy_strategy._previous_step
        return copy_strategy

    # brief: gets difference of rate between last buy-rate and current sell-rate
    # return: the difference of rate between last buy-rate and current sell-rate
    def GetDifferenceBetweenRate(self):
        difference_between_rate = None
        if self._previous_step:
            difference_between_rate = self._sell_rate - self._previous_step._buy_rate
        else:
            difference_between_rate = self._sell_rate - self._init_rate
        return difference_between_rate

    # brief: compute sell-rate of strategy-trade for current strategy-step for desired profit
    # param: sell_quantity - target quantity of sell-currency
    # param: sell_cost - desired cost of sell
    # return: trade-rate for sell
    def ComputeSellRate(self, sell_quantity, sell_cost):
        return self._RoundUp(sell_cost / (self._commission * sell_quantity))

    # brief: saves trade-strategy in file
    # note1: current trade-step will be saved too
    # param: filepath - full path to save-file
    def SaveToFile(self, filepath):
        first_step = self
        while first_step._previous_step:
            first_step = first_step._previous_step
        saved_params = {
            repr(const.INFO.STEP) : self._step,
            const.INFO.GLOBAL.PRICE_PRECISION : str(first_step._price_precision).count('0'),
            const.INFO.GLOBAL.VOLUME_PRECISION : str(first_step._volume_precision).count('0'),
            const.INFO.GLOBAL.COEFFICIENT : first_step._coefficient,
            const.INFO.GLOBAL.COMMISSION : first_step._commission,
            const.INFO.GLOBAL.PROFIT : first_step._profit,
            const.INFO.STEP.AVERAGE_RATE : first_step._init_rate,
            const.INFO.STEP.TOTAL_BUY_COST : first_step._init_cost,
        }
        faf.SaveContentToFile1(filepath, json.dumps(saved_params, indent=4))

    # param: getted full information about current step of the trading-strategy
    # return: full information about trading-strategy
    def GetInfo(self):
        info = {
            const.INFO.GLOBAL : {
                const.INFO.GLOBAL.COMMISSION : {
                    const.INFO.VALUE : self._commission,
                    const.INFO.DESCRIPTION : "commission for buy/sale transactions imposed by the trading-exchange"
                },
                const.INFO.GLOBAL.PRICE_PRECISION : {
                    const.INFO.VALUE : self._price_precision,
                    const.INFO.DESCRIPTION : "precision for computing of trade-rate"
                },
                const.INFO.GLOBAL.VOLUME_PRECISION : {
                    const.INFO.VALUE : self._volume_precision,
                    const.INFO.DESCRIPTION : "precision for computing of currency-volume"
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
                        "description" : "total currency cost at the current trading-strategy step"
                    },
                    const.INFO.GLOBAL.COST.TOTAL_REAL : {
                        "value" : self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL],
                        "description" : "real currency cost at the current trading-strategy step"
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
                const.INFO.STEP.AVERAGE_RATE : {
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
                    const.INFO.VALUE : self.ComputeSellRate(self._sell_quantity, self._init_cost * 1.0),
                    const.INFO.DESCRIPTION : "currency-sell-rate need for realized 0%-profit of the trading-strategy"
                },
                const.INFO.STEP.NEXT_BUY_RATE : {
                    const.INFO.VALUE : self._buy_rate,
                    const.INFO.DESCRIPTION : "maximum currency buy-rate need for going to next step of the current trading-strategy"
                },
                const.INFO.STEP.NEXT_BUY_COST : {
                    const.INFO.VALUE : self._buy_cost,
                    const.INFO.DESCRIPTION : "cost of currency for next buy-step of the current trading-strategy"
                },
            },
        }
        return info

    # brief: gets current trade-strategy step
    # return: current trade-strategy step
    def GetStep(self):
        return self._step

    # brief: restore trade-strategy from file
    # note1: saved trade-step will be restored too
    # param: filepath - full path to restore-file
    @classmethod
    def RestoreFromFile(cls, filepath):
        restored_params = json.loads(faf.GetFileContent(filepath))
        restored_strategy = cls()
        restored_strategy.SetPricePrecision1(restored_params[const.INFO.GLOBAL.PRICE_PRECISION])
        restored_strategy.SetVolumePrecision1(restored_params[const.INFO.GLOBAL.VOLUME_PRECISION])
        restored_strategy.SetCoefficient(restored_params[const.INFO.GLOBAL.COEFFICIENT])
        restored_strategy.SetCommission(restored_params[const.INFO.GLOBAL.COMMISSION])
        restored_strategy.SetProfit(restored_params[const.INFO.GLOBAL.PROFIT])
        restored_strategy.Init(restored_params[const.INFO.STEP.AVERAGE_RATE], restored_params[const.INFO.STEP.TOTAL_BUY_COST])
        return restored_strategy.ComputeToStep(restored_params[repr(const.INFO.STEP)])

    # brief: get strategy-ID
    # return: strategy-ID
    @staticmethod
    def GetID():
        return const.ID.STAIRS_SIMPLE
