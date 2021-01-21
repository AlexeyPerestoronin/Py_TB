import math
import copy
import json
import decimal

import strategy
import common.faf as faf
import strategy.const as const
import strategy.const.errors as error

_d = decimal.Decimal

# brief: implements simple strairs trade-strategy
class Simple:
    def __init__(self):
        # flags(s)
        self._is_initialized = False
        # global(s)
        self._price_precision = None
        self._quantity_precision = None
        self._step_coefficient = None
        self._init_coefficient = None
        self._profit = None
        self._total_available_currency = None
        self._current_available_currency = None
        # init(s)
        self._init_rate = None
        self._init_cost = None
        # sell(s)
        self._sell_cost = None
        self._sell_rate = None
        self._sell_quantity = None
        self._sell_commission = None
        # buy(s)
        self._buy_cost = None
        self._buy_rate = None
        self._buy_quantity = None
        self._buy_commission = None
        # steps(s)
        self._step = None
        self._first_step = None
        self._next_step = None
        self._previous_step = None
        # statistic(s)
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
        # precision(s)
        self._PPU = None
        self._PPD = None
        self._QPU = None
        self._QPD = None

    # brief: creates dictionary with recovery parameters by which is possible restore trade-strategy to current state
    # return: recovery dictionary
    def _CreateRecoveryParameters(self):
        recovery_params = {
            repr(const.INFO.STEP) : self._step,
            const.INFO.STEP.AVAILABLE_CURRENCY : self._first_step._total_available_currency,
            const.INFO.GLOBAL.PRICE_PRECISION : str(self._first_step._price_precision).count('0'),
            const.INFO.GLOBAL.QUANTITY_PRECISION : str(self._first_step._quantity_precision).count('0'),
            const.INFO.GLOBAL.COEFFICIENT : self._first_step._init_coefficient,
            const.INFO.GLOBAL.BUY_COMMISSION : self._first_step._buy_commission,
            const.INFO.GLOBAL.SELL_COMMISSION : self._first_step._sell_commission,
            const.INFO.GLOBAL.PROFIT : self._first_step._profit,
            const.INFO.STEP.AVERAGE_RATE : self._first_step._init_rate,
            const.INFO.STEP.TOTAL_BUY_COST : self._first_step._init_cost,
        }
        return recovery_params

    # brief: restores trade-strategy state by recovery parameters
    # note1: the recovery parameters must be creates by cls._CreateRecoveryParameters function
    # param: recovery_params - target recovery parameters
    # return: restored trade-strategy
    @classmethod
    def _RestoreFromRecoveryParameters(cls, recovery_params):
        restored_strategy = cls()
        restored_strategy.SetAvailableCurrency(recovery_params[const.INFO.STEP.AVAILABLE_CURRENCY])
        restored_strategy.SetPricePrecision1(recovery_params[const.INFO.GLOBAL.PRICE_PRECISION])
        restored_strategy.SetQuantityPrecision1(recovery_params[const.INFO.GLOBAL.QUANTITY_PRECISION])
        restored_strategy.SetCoefficient(recovery_params[const.INFO.GLOBAL.COEFFICIENT])
        restored_strategy.SetCommissionBuy(recovery_params[const.INFO.GLOBAL.BUY_COMMISSION])
        restored_strategy.SetCommissionSell(recovery_params[const.INFO.GLOBAL.SELL_COMMISSION])
        restored_strategy.SetProfit(recovery_params[const.INFO.GLOBAL.PROFIT])
        restored_strategy.Init(recovery_params[const.INFO.STEP.AVERAGE_RATE], recovery_params[const.INFO.STEP.TOTAL_BUY_COST])
        return restored_strategy.ComputeToStep(recovery_params[repr(const.INFO.STEP)])

    # collects statistic for all steps of trade-strategy
    def _CollectStatistic(self):
        if not self._previous_step:
            clean_quantity = self._init_cost / self._init_rate
            real_quantity = clean_quantity * self._buy_commission
            real_quantity = self._QPD(real_quantity)
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
            real_quantity = clean_quantity * self._previous_step._buy_commission
            real_quantity = self._QPD(real_quantity)
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

    # brief: compute next coefficient for buy-cost
    # return: next coefficient
    def _ComputeNextCoefficient(self):
        self._step_coefficient = self._init_coefficient

    # brief: compute sell-cost for current strategy-step to sell-action
    def _ComputeSellCost(self):
        self._sell_cost = self._PPD(self._sell_quantity * self._sell_rate)

    # brief: compute sell-rate for current strategy-step to sell-action
    def _ComputeSellRate(self):
        self._sell_rate = self.ComputeSellRate(self._sell_quantity, self._init_cost * self._profit)

    # brief: compute sell-quantity for current-strategy-step to sell-action
    def _ComputeSellQuantity(self):
        self._sell_quantity = self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_REAL]

    # brief: compute buy-cost for current strategy-step to buy-action
    def _ComputeBuyCost(self):
        self._buy_cost = self._init_cost * self._step_coefficient

    # brief: compute buy-rate for current strategy-step to buy-action
    def _ComputeBuyRate(self):
        sell_rate = self._GetNextSellRate()
        self._current_available_currency -= self._buy_cost
        if self._current_available_currency < 0.:
            raising_error = error.ExceededAvailableCurrency()
            raising_error.SetSellQuantity(self._sell_quantity)
            raising_error.SetSellCost(self._sell_cost)
            raising_error.SetSellRate(self._sell_rate)
            raise raising_error
        sell_cost = self._init_cost + self._buy_cost
        self._buy_rate = self._PPD(- (self._buy_cost * self._buy_commission) / (self._sell_quantity - ((self._profit * sell_cost) / (sell_rate * self._sell_commission))))
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
        # (buy) sequence of calculations
        self._ComputeBuyCost()
        self._ComputeBuyRate()
        self._ComputeBuyQuantity()

    # brief: set the coefficient of each next cost increaseble
    # param: coefficient - new each next cost increaseble
    def SetCoefficient(self, coefficient):
        self._init_coefficient = coefficient

    # brief: set a trade-commission for buy-order
    # param: buy_commission - new value of a trade-commission for buy-order
    def SetCommissionBuy(self, buy_commission):
        self._buy_commission = buy_commission

    # brief: set a trade-commission for sell-order
    # param: sell_commission - new value of a trade-commission for sell-order
    def SetCommissionSell(self, sell_commission):
        self._sell_commission = sell_commission

    # brief: set a trade-profit
    # param: profit - new value of a trade-profit
    def SetProfit(self, profit):
        self._profit = profit

    # brief: set a available currency
    # param: available_currency - new value of a available currency
    def SetAvailableCurrency(self, available_currency):
        self._current_available_currency = available_currency

    # brief: set a precision of all mathematical operations performs with volume of currency
    # param: precision - new value of a precision (must be positive integer number)
    def SetQuantityPrecision1(self, precision):
        self.SetQuantityPrecision2(self._ComputePrecision(precision))

    # brief: set a precision of all mathematical operations performs with volume of currency
    # param: precision - new value of a precision
    def SetQuantityPrecision2(self, precision):
        self._quantity_precision = _d(precision)
        self._QPU = lambda value: self._RoundUp(value, self._quantity_precision)
        self._QPD = lambda value: self._RoundDown(value, self._quantity_precision)

    # brief: set a precision of all mathematical operations performs with trade-rate
    # param: precision - new value of a precision (must be positive integer number)
    def SetPricePrecision1(self, precision):
        self.SetPricePrecision2(self._ComputePrecision(precision))

    # brief: set a precision of all mathematical operations performs with trade-rate
    # param: precision - new value of a precision
    def SetPricePrecision2(self, precision):
        self._price_precision = _d(precision)
        self._PPU = lambda value: self._RoundUp(value, self._price_precision)
        self._PPD = lambda value: self._RoundDown(value, self._price_precision)

    # brief: strategy initialization
    # note1: this function must be called only after call of SetCoefficient, SetCommission and SetProfit functions
    # param: rate - currency rate on first-step
    # param: cost - currency cost on first-step
    def Init(self, rate, cost):
        self._init_rate = self._PPU(rate)
        self._init_cost = cost
        self._step = 1
        if self._previous_step:
            self._step = self._previous_step._step + 1
            self._statistic = copy.deepcopy(self._previous_step._statistic)
        else:
            self._first_step = self
            self._total_available_currency = self._current_available_currency
            self._current_available_currency -= self._init_cost
            if self._current_available_currency < 0.:
                raise error.ExceededAvailableCurrency()
        self._ComputeCurrentStep()
        self._is_initialized = True

    # brief: check is strategy initialized
    # return: true - if is initialized; false - vise versa
    def IsInitialized(self):
        return self._is_initialized

    # brief: gets sell-cost for current step
    # return: the sell-cost for current step
    def GetSellCost(self):
        return self._sell_cost

    # brief: gets sell-rate for current step
    # return: the sell-rate for current step
    def GetSellRate(self):
        return self._sell_rate

    # brief: gets quantity for sell-order for current step
    # return: the quantity for sell-order for current step
    def GetSellQuantity(self):
        return self._sell_quantity

    # brief: gets buy-cost for current step
    # return: the buy-cost for current step
    def GetBuyCost(self):
        return self._buy_cost

    # brief: gets buy-rate for current step
    # return: the buy-rate for current step
    def GetBuyRate(self):
        return self._buy_rate

    # brief: gets buy-quantity for current step
    # return: the buy-quantity for current step
    def GetBuyQuantity(self):
        return self._buy_quantity

    # brief: compute next trade-step based of current trade-step
    # return: next trade-step
    def ComputeNextStep(self):
        self._next_step = type(self)()
        self._next_step._previous_step = self
        # migrate settings(1)
        self._next_step.SetAvailableCurrency(self._current_available_currency)
        self._next_step.SetQuantityPrecision2(self._quantity_precision)
        self._next_step.SetPricePrecision2(self._price_precision)
        self._next_step.SetCommissionSell(self._sell_commission)
        self._next_step.SetCommissionBuy(self._buy_commission)
        self._next_step.SetCoefficient(self._init_coefficient)
        self._next_step.SetProfit(self._profit)
        # compute cost and rate for next step (as if it is cost and rate for first step)
        cost = self._init_cost + self._buy_cost
        rate = (math.pow(self._buy_commission, 2) * self._GetNextSellRate()) / self._profit
        self._next_step._first_step = self._first_step
        self._next_step.Init(rate, cost)
        return self._next_step

    # brief: goes to the target-step in current trade-strategy
    # param: to_step - target trade-step
    # return: the trade strategy in target trade-step state
    def ComputeToStep(self, to_step):
        if self._first_step:
            copy_strategy = copy.deepcopy(self._first_step)
            for _ in range(1, to_step):
                copy_strategy = copy_strategy.ComputeNextStep()
            return copy_strategy
        else:
            raise error.NotInitializedStrategy()

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
        return self._PPU((sell_cost / self._sell_commission) / sell_quantity)

    # brief: gets string from which is possible restore trade-strategy to current state
    # return: trade-strategy restore string
    def CreateRecoveryString(self):
        return json.dumps(self._CreateRecoveryParameters())

    # brief: saves trade-strategy in file
    # note1: current trade-step will be saved too
    # param: filepath - full path to save-file
    def SaveToFile(self, filepath):
        faf.SaveContentToFile1(filepath, json.dumps(self._CreateRecoveryParameters(), indent=4))

    # param: getted full information about current step of the trading-strategy
    # return: full information about trading-strategy
    def GetInfo(self):
        info = {
            const.INFO.GLOBAL : {
                const.INFO.GLOBAL.TOTAL_AVAILABLE_CURRENCY : {
                    const.INFO.VALUE : self._first_step._total_available_currency,
                    const.INFO.DESCRIPTION : "total availbale currency for the trade-strategy"
                },
                const.INFO.GLOBAL.BUY_COMMISSION : {
                    const.INFO.VALUE : self._buy_commission,
                    const.INFO.DESCRIPTION : "commission for buy transactions imposed by the trading-exchange"
                },
                const.INFO.GLOBAL.SELL_COMMISSION : {
                    const.INFO.VALUE : self._sell_commission,
                    const.INFO.DESCRIPTION : "commission for sale transactions imposed by the trading-exchange"
                },
                const.INFO.GLOBAL.PRICE_PRECISION : {
                    const.INFO.VALUE : self._price_precision,
                    const.INFO.DESCRIPTION : "precision for computing of trade-rate"
                },
                const.INFO.GLOBAL.QUANTITY_PRECISION : {
                    const.INFO.VALUE : self._quantity_precision,
                    const.INFO.DESCRIPTION : "precision for computing of currency-volume"
                },
                const.INFO.GLOBAL.PROFIT : {
                    const.INFO.VALUE : self._profit,
                    const.INFO.DESCRIPTION : "profit realized by the trading-strategy"
                },
                const.INFO.GLOBAL.COEFFICIENT : {
                    const.INFO.VALUE : self._init_coefficient,
                    const.INFO.DESCRIPTION : "initial increase-cost-coefficient"
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
                const.INFO.STEP.AVAILABLE_CURRENCY : {
                    const.INFO.VALUE : self._current_available_currency,
                    const.INFO.DESCRIPTION : "residual amount of available currency for buy-order"
                },
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
                const.INFO.STEP.SELL_RATE_0 : {
                    const.INFO.VALUE : self.ComputeSellRate(self._sell_quantity, self._init_cost),
                    const.INFO.DESCRIPTION : "currency-rate for sell-order of the current step for zero-loss"
                },
                const.INFO.STEP.SELL_RATE : {
                    const.INFO.VALUE : self._sell_rate,
                    const.INFO.DESCRIPTION : "currency-rate for sell-order of the current step"
                },
                const.INFO.STEP.TOTAL_SELL_COST : {
                    const.INFO.VALUE : self._sell_cost,
                    const.INFO.DESCRIPTION : "total-sell-cost of currency in current step"
                },
                const.INFO.STEP.COEFFICIENT : {
                    const.INFO.VALUE : self._step_coefficient,
                    const.INFO.DESCRIPTION : "increase-cost-coefficient for buy-order of the current step"
                },
                const.INFO.STEP.BUY_COST : {
                    const.INFO.VALUE : self._buy_cost,
                    const.INFO.DESCRIPTION : "cost of currency for buy-order of the current step"
                },
                const.INFO.STEP.BUY_RATE : {
                    const.INFO.VALUE : self._buy_rate,
                    const.INFO.DESCRIPTION : "currency-rate for buy-order of the current step"
                },
            },
        }
        return info

    # brief: gets current trade-strategy step
    # return: current trade-strategy step
    def GetStep(self):
        return self._step

    # brief: restore trade-strategy from recovery-string
    # note1: saved trade-step will be restored too
    # param: filepath - full path to restore-file
    @classmethod
    def RestoreFromRecoveryString(cls, recovery_string):
        return cls._RestoreFromRecoveryParameters(json.loads(recovery_string))

    # brief: restore trade-strategy from file
    # note1: saved trade-step will be restored too
    # param: filepath - full path to restore-file
    @classmethod
    def RestoreFromFile(cls, filepath):
        return cls._RestoreFromRecoveryParameters(json.loads(faf.GetFileContent(filepath)))

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.STAIRS_SIMPLE

    # brief: round-up the number to predefined precision
    # param: number - target number for round
    # return: rounded number
    @staticmethod
    def _RoundUp(number, precision):
        return float(_d(number).quantize(precision, decimal.ROUND_CEILING))

    # brief: round-down the number to predefined precision
    # param: number - target number for round
    # return: rounded number
    @staticmethod
    def _RoundDown(number, precision):
        return float(_d(number).quantize(precision, decimal.ROUND_FLOOR))

    # brief: compute precision
    # param: precision - new value of a precision (must be positive integer number)
    @staticmethod
    def _ComputePrecision(precision):
        result = "1."
        for _ in range(precision):
            result+="0"
        return _d(result)
