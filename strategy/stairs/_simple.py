import math
import copy
import json
import decimal

import common.faf as faf
import common.precision as c_precision

import strategy.const as const
import strategy.const.errors as error

_d = decimal.Decimal

# brief: implements template for all simple strairs trade-strategy
class Simple:
    def __init__(self):
        # flags(s)
        self._is_initialized = False
        # steps(s)
        self._next_step = None
        self._first_step = None
        self._previous_step = None
        # setting(s)
        self._parameters = {
            # global(s)
            const.PARAMS.GLOBAL_COST_PRECISION : None,
            const.PARAMS.GLOBAL_RATE_PRECISION : None,
            const.PARAMS.GLOBAL_QUANTITY_PRECISION : None,
            const.PARAMS.GLOBAL_COEFFICIENT_1 : None,
            const.PARAMS.GLOBAL_COEFFICIENT_2 : None,
            const.PARAMS.GLOBAL_COEFFICIENT_3 : None,
            const.PARAMS.GLOBAL_COEFFICIENT_4 : None,
            const.PARAMS.GLOBAL_COEFFICIENT_5 : None,
            const.PARAMS.GLOBAL_PROFIT : None,
            const.PARAMS.GLOBAL_AVAILABLE_CURRENCY : None,
            const.PARAMS.GLOBAL_SELL_COMMISSION : None,
            const.PARAMS.GLOBAL_SELL_COMMISSION_CONCESSION : None,
            const.PARAMS.GLOBAL_BUY_COMMISSION : None,
            const.PARAMS.GLOBAL_BUY_COMMISSION_CONCESSION : None,
            # init(s)
            const.PARAMS.INIT_RATE : None,
            const.PARAMS.INIT_COST : None,
            # steps(s)
            const.PARAMS.STEP : None,
            const.PARAMS.STEP_COEFFICIENT_1 : None,
            const.PARAMS.STEP_COEFFICIENT_2 : None,
            const.PARAMS.STEP_COEFFICIENT_3 : None,
            const.PARAMS.STEP_COEFFICIENT_4 : None,
            const.PARAMS.STEP_COEFFICIENT_5 : None,
            const.PARAMS.STEP_AVAILABLE_CURRENCY : None,
            # sell(s)
            const.PARAMS.STEP_SELL_COST : None,
            const.PARAMS.STEP_SELL_RATE : None,
            const.PARAMS.STEP_SELL_PROFIT : None,
            const.PARAMS.STEP_SELL_QUANTITY : None,
            # buy(s)
            const.PARAMS.STEP_BUY_COST : None,
            const.PARAMS.STEP_BUY_RATE : None,
            const.PARAMS.STEP_BUY_QUANTITY : None,
        }
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
        self._CP = None
        self._RP = None
        self._QP = None

    # brief: initializes classes for precision computing
    def _InitPrecisions(self):
        if not self._CP:
            self._RP = c_precision.Round(self._parameters[const.PARAMS.GLOBAL_COST_PRECISION])
        if not self._RP:
            self._RP = c_precision.Round(self._parameters[const.PARAMS.GLOBAL_RATE_PRECISION])
        if not self._QP:
            self._QP = c_precision.Round(self._parameters[const.PARAMS.GLOBAL_QUANTITY_PRECISION])

    # brief: creates dictionary with recovery parameters by which is possible restore trade-strategy to current state
    # return: recovery dictionary
    def _CreateRecoveryParameters(self):
        recovery_params = {}
        for key, value in self._first_step._parameters.items():
            recovery_params[key] = str(value)
        recovery_params[const.PARAMS.STEP] = self._parameters[const.PARAMS.STEP]
        return recovery_params

    # brief: restores trade-strategy state by recovery parameters
    # note1: the recovery parameters must be creates by cls._CreateRecoveryParameters function
    # param: recovery_params - target recovery parameters
    # return: restored trade-strategy
    @classmethod
    def _RestoreFromRecoveryParameters(cls, recovery_params):
        restored_strategy = cls()
        for key, value in recovery_params.items():
            assigned_value = None
            if value != "None":
                assigned_value = _d(value)
            restored_strategy._parameters[key] = assigned_value
        restored_strategy.Init(recovery_params[const.PARAMS.INIT_RATE], recovery_params[const.PARAMS.INIT_COST])
        return restored_strategy.ComputeToStep(recovery_params[const.PARAMS.STEP])

    # collects statistic for all steps of trade-strategy
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
        clean_quantity = self._QP.DownDecimal(total_buy_cost / total_buy_rate)
        real_quantity = self._QP.DownDecimal(clean_quantity * buy_commission)
        lost_quantity = self._QP.DownDecimal(clean_quantity - real_quantity)
        self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_CLEAN] += clean_quantity
        self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_REAL] += real_quantity
        self._statistic[const.INFO.GLOBAL.VOLUME][const.INFO.GLOBAL.VOLUME.TOTAL_LOST] += lost_quantity
        # collection of statistics (cost)
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CLEAN] += total_buy_cost
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_REAL] += real_quantity * total_buy_rate
        self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_LOST] += lost_quantity * total_buy_rate

    # brief: compute next coefficient-1
    # note1: must be redefined in child class if it is need
    def _ComputeNextCoefficient1(self):
        self._parameters[const.PARAMS.STEP_COEFFICIENT_1] = self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_1]

    # brief: compute next coefficient-2
    # note1: must be redefined in child class if it is need
    def _ComputeNextCoefficient2(self):
        self._parameters[const.PARAMS.STEP_COEFFICIENT_2] = self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_2]

    # brief: compute next coefficient-3
    # note1: must be redefined in child class if it is need
    def _ComputeNextCoefficient3(self):
        self._parameters[const.PARAMS.STEP_COEFFICIENT_3] = self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_3]

    # brief: compute next coefficient-4
    # note1: must be redefined in child class if it is need
    def _ComputeNextCoefficient4(self):
        self._parameters[const.PARAMS.STEP_COEFFICIENT_4] = self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_4]

    # brief: compute next coefficient-5
    # note1: must be redefined in child class if it is need
    def _ComputeNextCoefficient5(self):
        self._parameters[const.PARAMS.STEP_COEFFICIENT_5] = self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_5]

    # brief: gets sell-rate for next-step
    # note1: must be redefined in child class
    # return: the sell-rate for next-step
    def _GetNextSellRate(self):
        raise error.MethodIsNotImplemented()

    # brief: compute sell-cost for current strategy-step to sell-action
    # note1: must be redefined in child class
    def _ComputeSellCost(self):
        raise error.MethodIsNotImplemented()

    # brief: compute sell-profit for current strategy-step to sell-action
    # note1: must be redefined in child class
    def _ComputeSellProfit(self):
        raise error.MethodIsNotImplemented()

    # brief: compute sell-rate for current strategy-step to sell-action
    # note1: must be redefined in child class
    def _ComputeSellRate(self):
        raise error.MethodIsNotImplemented()

    # brief: compute sell-quantity for current-strategy-step to sell-action
    # note1: must be redefined in child class
    def _ComputeSellQuantity(self):
        raise error.MethodIsNotImplemented()

    # brief: compute buy-cost for current strategy-step to buy-action
    # note1: must be redefined in child class
    def _ComputeBuyCost(self):
        raise error.MethodIsNotImplemented()

    # brief: compute buy-rate for current strategy-step to buy-action
    # note1: must be redefined in child class
    def _ComputeBuyRate(self):
        raise error.MethodIsNotImplemented()

    # brief: compute buy-quantity for current strategy-step to buy-action
    # note1: must be redefined in child class
    def _ComputeBuyQuantity(self):
        raise error.MethodIsNotImplemented()

    # brief: compute sell and buy parameters for current strategy-step
    # note1: must be redefined in child class
    def _ComputeSellAndBuyParameters(self):
        raise error.MethodIsNotImplemented()

    # brief: compute current strategy-step
    def _ComputeCurrentStep(self):
        self._CollectStatistic()
        # sequence of calculations 1: ceff
        self._ComputeNextCoefficient1()
        self._ComputeNextCoefficient2()
        self._ComputeNextCoefficient3()
        self._ComputeNextCoefficient4()
        self._ComputeNextCoefficient5()
        # sequence of calculations 2: sell and buy params
        self._ComputeSellAndBuyParameters()

    # brief: migrates settings of current strategy to a new next strategy class
    def _MigrateSettingsToNextStep(self):
        self._next_step = type(self)()
        # migrate step 1: precission(s)
        self._next_step._CP = self._CP
        self._next_step._RP = self._RP
        self._next_step._QP = self._QP
        # migrate step 2: step(s)
        self._next_step._previous_step = self
        self._next_step._first_step = self._first_step
        # migrate step 3: step settings(s)
        self._next_step._statistic = copy.deepcopy(self._statistic)
        self._next_step._parameters = copy.deepcopy(self._parameters)

    # brief: strategy initialization
    # param: rate - currency rate on first-step
    # param: cost - currency cost on first-step
    def Init(self, rate, cost):
        self._InitPrecisions()
        self._parameters[const.PARAMS.INIT_RATE] = self._RP.UpDecimal(_d(rate))
        self._parameters[const.PARAMS.INIT_COST] = self._CP.DownDecimal(_d(cost))
        if self._previous_step:
            self._parameters[const.PARAMS.STEP] += 1
        else:
            self._first_step = self
            self._parameters[const.PARAMS.STEP] = 1
            global_currency = self._parameters[const.PARAMS.GLOBAL_AVAILABLE_CURRENCY]
            total_buy_currency = self._parameters[const.PARAMS.INIT_COST]
            step_available_currency = global_currency - total_buy_currency
            if step_available_currency < 0.:
                raise error.ExceededAvailableCurrency()
            self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY] = step_available_currency
        self._ComputeCurrentStep()
        self._is_initialized = True

    # NOTE: Set...

    # brief: set the 1-coefficient
    # param: coefficient - new value for 1-coefficient
    def SetCoefficient1(self, coefficient):
        self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_1] = _d(coefficient)

    # brief: set the 2-coefficient
    # param: coefficient - new value for 2-coefficient
    def SetCoefficient2(self, coefficient):
        self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_2] = _d(coefficient)

    # brief: set the 3-coefficient
    # param: coefficient - new value for 3-coefficient
    def SetCoefficient3(self, coefficient):
        self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_3] = _d(coefficient)

    # brief: set the 4-coefficient
    # param: coefficient - new value for 4-coefficient
    def SetCoefficient4(self, coefficient):
        self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_4] = _d(coefficient)

    # brief: set the 5-coefficient
    # param: coefficient - new value for 5-coefficient
    def SetCoefficient5(self, coefficient):
        self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_5] = _d(coefficient)

    # brief: set a trade-commission for buy-order
    # param: buy_commission - new value of a trade-commission for buy-order
    # param: buy_commission_concession - new value of concession of a trade-commission for buy-order
    def SetCommissionBuy(self, buy_commission, buy_commission_concession=0.5):
        self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION] = _d(buy_commission)
        self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION_CONCESSION] = _d(buy_commission_concession)

    # brief: set a trade-commission for sell-order
    # param: sell_commission - new value of a trade-commission for sell-order
    # param: sell_commission_concession - new value of concession of a trade-commission for sell-order
    def SetCommissionSell(self, sell_commission, sell_commission_concession=0.5):
        self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION] = _d(sell_commission)
        self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION_CONCESSION] = _d(sell_commission_concession)

    # brief: set a trade-profit
    # param: profit - new value of a trade-profit
    def SetProfit(self, profit):
        self._parameters[const.PARAMS.GLOBAL_PROFIT] = _d(profit)

    # brief: set a available currency
    # param: available_currency - new value of a available currency
    def SetAvailableCurrency(self, available_currency):
        self._parameters[const.PARAMS.GLOBAL_AVAILABLE_CURRENCY] = self._CP.DownDecimal(_d(available_currency))

    # brief: set a precision of all mathematical operations performs with trade-cost
    # param: precision - new value of a precision
    def SetCostPrecision(self, precision):
        self._parameters[const.PARAMS.GLOBAL_COST_PRECISION] = _d(precision)
    
    # brief: set a precision of all mathematical operations performs with trade-rate
    # param: precision - new value of a precision
    def SetRatePrecision(self, precision):
        self._parameters[const.PARAMS.GLOBAL_RATE_PRECISION] = _d(precision)
    
    # brief: set a precision of all mathematical operations performs with volume of currency
    # param: precision - new value of a precision
    def SetQuantityPrecision(self, precision):
        self._parameters[const.PARAMS.GLOBAL_QUANTITY_PRECISION] = _d(precision)

    # NOTE: Get...

    # brief: gets current trade-strategy step
    # return: current trade-strategy step
    def GetStep(self):
        return self._parameters[const.PARAMS.STEP]

    # brief: gets sell-profit for current trade-strategy step
    # return: current sell-profit
    def GetStepProfit(self):
        return self._parameters[const.PARAMS.STEP_SELL_PROFIT]

    # brief: gets sell-cost for current step
    # return: the sell-cost for current step
    def GetSellCost(self):
        return self._parameters[const.PARAMS.STEP_SELL_COST]

    # brief: gets sell-rate for current step
    # return: the sell-rate for current step
    def GetSellRate(self):
        return self._parameters[const.PARAMS.STEP_SELL_RATE]

    # brief: gets quantity for sell-order for current step
    # return: the quantity for sell-order for current step
    def GetSellQuantity(self):
        return self._parameters[const.PARAMS.STEP_SELL_QUANTITY]

    # brief: gets profit for sell-order for current step
    # return: the profit for sell-order for current step
    def GetSellProfit(self):
        return self._parameters[const.PARAMS.STEP_SELL_PROFIT]

    # brief: gets buy-cost for current step
    # return: the buy-cost for current step
    def GetBuyCost(self):
        return self._parameters[const.PARAMS.STEP_BUY_COST]

    # brief: gets buy-rate for current step
    # return: the buy-rate for current step
    def GetBuyRate(self):
        return self._parameters[const.PARAMS.STEP_BUY_RATE]

    # brief: gets buy-quantity for current step
    # return: the buy-quantity for current step
    def GetBuyQuantity(self):
        return self._parameters[const.PARAMS.STEP_BUY_QUANTITY]

    # brief: gets total-buy-cost of currency in current-step
    # return: total-buy-cost in current-step
    def GetTotalBuyCost(self):
        return self._parameters[const.PARAMS.INIT_COST]

    # brief: gets total-everage-buy-rate of currency in current-step
    # return: total-everage-buy-rate in current-step
    def GetTotalEverageBuyRate(self):
        return self._parameters[const.PARAMS.INIT_RATE]

    # brief: gets difference of rate between last buy-rate and current sell-rate
    # return: the difference of rate between last buy-rate and current sell-rate
    def GetDifferenceBetweenRate(self):
        difference_between_rate = None
        if self._previous_step:
            difference_between_rate = self._parameters[const.PARAMS.STEP_SELL_RATE] - self._previous_step._parameters[const.PARAMS.STEP_BUY_RATE]
        else:
            difference_between_rate = self._parameters[const.PARAMS.STEP_SELL_RATE] - self._parameters[const.PARAMS.INIT_RATE]
        return difference_between_rate

    # param: getted full information about current step of the trading-strategy
    # return: full information about trading-strategy
    def GetInfo(self):
        info = {
            const.INFO.GLOBAL : {
                const.INFO.GLOBAL.TOTAL_AVAILABLE_CURRENCY : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.GLOBAL_AVAILABLE_CURRENCY],
                    const.INFO.DESCRIPTION : "total availbale currency for the trade-strategy"
                },
                const.INFO.GLOBAL.BUY_COMMISSION : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION],
                    const.INFO.DESCRIPTION : "commission for buy transactions imposed by the trading-exchange"
                },
                const.INFO.GLOBAL.SELL_COMMISSION : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION],
                    const.INFO.DESCRIPTION : "commission for sale transactions imposed by the trading-exchange"
                },
                const.INFO.GLOBAL.PRICE_PRECISION : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.GLOBAL_RATE_PRECISION],
                    const.INFO.DESCRIPTION : "precision for computing of trade-rate"
                },
                const.INFO.GLOBAL.QUANTITY_PRECISION : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.GLOBAL_QUANTITY_PRECISION],
                    const.INFO.DESCRIPTION : "precision for computing of currency-volume"
                },
                const.INFO.GLOBAL.PROFIT : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.GLOBAL_PROFIT],
                    const.INFO.DESCRIPTION : "profit realized by the trading-strategy"
                },
                const.INFO.GLOBAL.COEFFICIENT : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_1],
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
                    const.INFO.VALUE : self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY],
                    const.INFO.DESCRIPTION : "residual amount of available currency for buy-order"
                },
                const.INFO.STEP.DIFFERENCE_RATE : {
                    const.INFO.VALUE : self.GetDifferenceBetweenRate(),
                    const.INFO.DESCRIPTION : "the difference between last buy-rate and current sell-rate"
                },
                const.INFO.STEP.AVERAGE_RATE : {
                    const.INFO.VALUE : self.GetTotalEverageBuyRate(),
                    const.INFO.DESCRIPTION : "total-everage-buy-rate is buy-rate of currency on total-cost at the in current step"
                },
                const.INFO.STEP.TOTAL_BUY_COST : {
                    const.INFO.VALUE : self.GetTotalBuyCost(),
                    const.INFO.DESCRIPTION : "total-buy-cost of currency in current step"
                },
                const.INFO.STEP.SELL_RATE_0 : {
                    const.INFO.VALUE : self.ComputeSellRate(self._parameters[const.PARAMS.STEP_SELL_QUANTITY], self._parameters[const.PARAMS.INIT_COST]),
                    const.INFO.DESCRIPTION : "currency-rate for sell-order of the current step for zero-loss"
                },
                const.INFO.STEP.SELL_RATE : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.STEP_SELL_RATE],
                    const.INFO.DESCRIPTION : "currency-rate for sell-order of the current step"
                },
                const.INFO.STEP.TOTAL_SELL_COST : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.STEP_SELL_COST],
                    const.INFO.DESCRIPTION : "total-sell-cost of currency in current step"
                },
                const.INFO.STEP.TOTAL_SELL_PROFIT : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.STEP_SELL_PROFIT],
                    const.INFO.DESCRIPTION : "total-sell-profit of currency in current step"
                },
                const.INFO.STEP.COEFFICIENT : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.STEP_COEFFICIENT_1],
                    const.INFO.DESCRIPTION : "increase-cost-coefficient for buy-order of the current step"
                },
                const.INFO.STEP.BUY_COST : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.STEP_BUY_COST],
                    const.INFO.DESCRIPTION : "cost of currency for buy-order of the current step"
                },
                const.INFO.STEP.BUY_RATE : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.STEP_BUY_RATE],
                    const.INFO.DESCRIPTION : "currency-rate for buy-order of the current step"
                },
            },
        }
        return info

    # NOTE: Is...

    # brief: check is strategy initialized
    # return: true - if is initialized; false - vise versa
    def IsInitialized(self):
        return self._is_initialized

    # NOTE: Compute...

    # brief: compute the next-step regarding current trade-strategy
    # return: deep copy of the current trade-strategy presented on the next-step
    def ComputeNextStep(self):
        self._MigrateSettingsToNextStep()
        # compute cost and rate for next step (as if it is cost and rate for first step)
        next_sell_rate = self._GetNextSellRate()
        buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION]
        profit = self._parameters[const.PARAMS.GLOBAL_PROFIT]
        total_buy_cost = self._parameters[const.PARAMS.INIT_COST] + self._parameters[const.PARAMS.STEP_BUY_COST]
        everage_buy_rate = self._RP.UpDecimal(buy_commission**2 * next_sell_rate / profit)
        self._next_step.Init(everage_buy_rate, total_buy_cost)
        return self._next_step

    # brief: compute the specified-step regarding current trade-strategy
    # param: to_step - target trade-step
    # return: deep copy of the current trade-strategy presented on the specified-step
    def ComputeToStep(self, to_step):
        if self._first_step:
            copy_strategy = copy.deepcopy(self._first_step)
            for _ in range(1, to_step):
                copy_strategy = copy_strategy.ComputeNextStep()
            return copy_strategy
        else:
            raise error.NotInitializedStrategy()

    # brief: compute sell-rate of strategy-trade for current strategy-step for desired profit
    # param: sell_quantity - target quantity of sell-currency
    # param: sell_cost - desired cost of sell
    # return: trade-rate for sell
    def ComputeSellRate(self, sell_quantity, sell_cost):
        sell_commission = self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION]
        return (sell_cost / sell_commission) / sell_quantity

    # NOTE: Create...

    # brief: gets string from which is possible restore trade-strategy to current state
    # return: trade-strategy restore string
    def CreateRecoveryString(self):
        return json.dumps(self._CreateRecoveryParameters())

    # NOTE: Others methods

    # brief: saves trade-strategy in file
    # note1: current trade-step will be saved too
    # param: filepath - full path to save-file
    def SaveToFile(self, filepath):
        faf.SaveContentToFile1(filepath, json.dumps(self._CreateRecoveryParameters(), indent=4))

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
        return const.ID.Simple
