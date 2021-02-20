import math
import copy
import json
import decimal

import common
import common.faf as faf
import common.precision as c_precision

import strategy.const as const
import strategy.const.errors as error

_d = decimal.Decimal

# brief: implements template for all simple strairs trade-strategy
class StairsBase:
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
            const.PARAMS.INIT_QUANTITY : None,
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
            const.PARAMS.STEP_SELL_QUANTITY : None,
            # buy(s)
            const.PARAMS.STEP_BUY_COST : None,
            const.PARAMS.STEP_BUY_RATE : None,
            const.PARAMS.STEP_BUY_QUANTITY : None,
            # profit(s)
            const.PARAMS.STEP_LEFT_PROFIT : None,
            const.PARAMS.STEP_RIGHT_PROFIT : None,
        }
        self._statistic = {
            const.INFO.GLOBAL.COST : {
                const.INFO.GLOBAL.COST.TOTAL_CLEAN : _d(0),
                const.INFO.GLOBAL.COST.TOTAL_REAL : _d(0),
                const.INFO.GLOBAL.COST.TOTAL_LOST : _d(0),
                const.INFO.GLOBAL.COST.TOTAL_CONCESSION : _d(0),
            },
            const.INFO.GLOBAL.QUANTITY : {
                const.INFO.GLOBAL.QUANTITY.TOTAL_CLEAN : _d(0),
                const.INFO.GLOBAL.QUANTITY.TOTAL_REAL : _d(0),
                const.INFO.GLOBAL.QUANTITY.TOTAL_LOST : _d(0),
                const.INFO.GLOBAL.QUANTITY.TOTAL_CONCESSION : _d(0),
            }
        }
        # precision(s)
        self._CP = None
        self._RP = None
        self._QP = None

    # brief: initializes classes for precision computing
    def _InitPrecisions(self):
        if not self._CP:
            self._CP = c_precision.Round(self._parameters[const.PARAMS.GLOBAL_COST_PRECISION])
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
        restored_strategy.SetAllParametersFromDict(recovery_params)
        restored_strategy.Init()
        return restored_strategy.ComputeToStep(recovery_params[const.PARAMS.STEP])

    # collects statistic for all steps of trade-strategy
    # note1: must be redefined in child class
    def _CollectStatistic(self):
        raise error.MethodIsNotImplemented()

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

    # brief: gets buy-rate for next-step
    # note1: must be redefined in child class
    # return: the buy-rate for next-step
    def _GetNextBuyRate(self):
        raise error.MethodIsNotImplemented()

    # brief: gets sell-rate for next-step
    # note1: must be redefined in child class
    # return: the sell-rate for next-step
    def _GetNextSellRate(self):
        raise error.MethodIsNotImplemented()

    # brief: compute sell-cost for current strategy-step to sell-action
    # note1: must be redefined in child class
    def _ComputeSellCost(self):
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

    # brief: compute left-profit for current strategy-step
    # note1: must be redefined in child class
    def _ComputeLeftProfit(self):
        raise error.MethodIsNotImplemented()

    # brief: compute right-profit for current strategy-step
    # note1: must be redefined in child class
    def _ComputeRightProfit(self):
        raise error.MethodIsNotImplemented()

    # brief: compute sell and buy parameters for current strategy-step
    # note1: must be redefined in child class
    def _ComputeSellAndBuyParameters(self):
        raise error.MethodIsNotImplemented()

    # brief: reduction sell and buy parameters by its precision value
    # note1: must be redefined in child class
    def _ReductionPrecisionForSellAndBuyParameters(self):
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
        # sequence of calculations 3: reduction sell and buy parameters by its precision value
        self._ReductionPrecisionForSellAndBuyParameters()

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

    # brief: initializing next step of trade-strategy
    def _InitializeNextStep(self):
        raise error.MethodIsNotImplemented()

    # brief: initializing first step of trade-strategy
    def _InitializeFirstStep(self):
        raise error.MethodIsNotImplemented()

    # brief: strategy initialization
    def Init(self):
        self._InitPrecisions()
        if self._previous_step:
            self._parameters[const.PARAMS.STEP] += 1
        else:
            self._InitializeFirstStep()
            self._first_step = self
        self._ComputeCurrentStep()
        self._is_initialized = True

    # NOTE: Set...

    # brief: sets initialization rate
    # param: init_rate - the new value of initialization rate
    def SetInitRate(self, init_rate):
        self._parameters[const.PARAMS.INIT_RATE] =_d(init_rate)

    # brief: sets initialization cost
    # param: init_cost - the new value of initialization cost
    def SetInitCost(self, init_cost):
        self._parameters[const.PARAMS.INIT_COST] =_d(init_cost)

    # brief: sets initialization quantity
    # param: init_quantity - the new value of initialization quantity
    def SetInitQuantity(self, init_quantity):
        self._parameters[const.PARAMS.INIT_QUANTITY] =_d(init_quantity)

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
        if not self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION_CONCESSION]:
            self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION_CONCESSION] = _d(buy_commission_concession)

    # brief: set a trade-commission for sell-order
    # param: sell_commission - new value of a trade-commission for sell-order
    # param: sell_commission_concession - new value of concession of a trade-commission for sell-order
    def SetCommissionSell(self, sell_commission, sell_commission_concession=0.5):
        self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION] = _d(sell_commission)
        if not self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION_CONCESSION]:
            self._parameters[const.PARAMS.GLOBAL_SELL_COMMISSION_CONCESSION] = _d(sell_commission_concession)

    # brief: set a trade-profit
    # param: profit - new value of a trade-profit
    def SetProfit(self, profit):
        self._parameters[const.PARAMS.GLOBAL_PROFIT] = _d(profit)

    # brief: set a available currency
    # param: available_currency - new value of a available currency
    def SetAvailableCurrency(self, available_currency):
        self._parameters[const.PARAMS.GLOBAL_AVAILABLE_CURRENCY] = _d(available_currency)

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

    # brief: set all parameters for the strategy from dictionary
    # param: parameters - the assign parameters
    def SetAllParametersFromDict(self, parameters):
        for key, value in parameters.items():
            assigned_value = None
            if value != "None":
                assigned_value = _d(value)
            self._parameters[key] = assigned_value

    # NOTE: Get...

    # brief: gets current trade-strategy step
    # return: current trade-strategy step
    def GetStep(self):
        return self._parameters[const.PARAMS.STEP]

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

    # brief: gets total-activity-cost of currency in current-step
    # return: total-activity-cost in current-step
    def GetTotalActivityCost(self):
        return self._parameters[const.PARAMS.INIT_COST]

    # brief: gets total-everage-activity-rate of currency in current-step
    # return: total-everage-activity-rate in current-step
    def GetTotalEverageActivityRate(self):
        return self._parameters[const.PARAMS.INIT_RATE]

    # brief: gets profit for current trade-strategy step in left currency
    # return: current profit
    def GetStepProfitLeft(self):
        return self._parameters[const.PARAMS.STEP_LEFT_PROFIT]

    # brief: gets profit for current trade-strategy step in right currency
    # return: current profit
    def GetStepProfitRight(self):
        return self._parameters[const.PARAMS.STEP_RIGHT_PROFIT]

    # brief: gets profit for current strategy in left currency
    # return: the profit
    def GetProfitLeft(self):
        return self.GetStepProfitLeft()

    # brief: gets profit for current strategy in right currency
    # note1: must be redefined in child class
    # return: the profit
    def GetProfitRight(self):
        return self.GetStepProfitRight()

    # brief: gets difference of rate between last two activity-rate
    # note1: must be redefined in child class
    # return: the difference of rate between last two activity-rate
    def GetDifferenceBetweenRate(self):
        raise error.MethodIsNotImplemented()

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
                const.INFO.GLOBAL.QUANTITY : {
                    const.INFO.GLOBAL.QUANTITY.TOTAL_CLEAN : {
                        const.INFO.VALUE : self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_CLEAN],
                        const.INFO.DESCRIPTION : "total-clean volume of currency at the beggining of the current step"
                    },
                    const.INFO.GLOBAL.QUANTITY.TOTAL_REAL : {
                        const.INFO.VALUE : self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_REAL],
                        const.INFO.DESCRIPTION : "total-real volume of currency at the beggining of the current step"
                    },
                    const.INFO.GLOBAL.QUANTITY.TOTAL_LOST : {
                        const.INFO.VALUE : self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_LOST],
                        const.INFO.DESCRIPTION : "total-lost volume of currency at the beggining of the current step"
                    },
                    const.INFO.GLOBAL.QUANTITY.TOTAL_CONCESSION : {
                        const.INFO.VALUE : self._statistic[const.INFO.GLOBAL.QUANTITY][const.INFO.GLOBAL.QUANTITY.TOTAL_CONCESSION],
                        const.INFO.DESCRIPTION : "total-concession of commission for volume of currency at the beggining of the current step"
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
                    const.INFO.GLOBAL.COST.TOTAL_CONCESSION : {
                        "value" : self._statistic[const.INFO.GLOBAL.COST][const.INFO.GLOBAL.COST.TOTAL_CONCESSION],
                        "description" : "concession cost at the current trading-strategy step"
                    },
                },
            },
            const.INFO.STEP : {
                const.INFO.STEP.DIFFERENCE_RATE : {
                    const.INFO.VALUE : self.GetDifferenceBetweenRate(),
                    const.INFO.DESCRIPTION : "the difference between last buy-rate and current sell-rate"
                },
                const.INFO.STEP.AVAILABLE_CURRENCY : {
                    const.INFO.VALUE : self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY],
                    const.INFO.DESCRIPTION : "residual amount of available currency for buy-order"
                },
                const.INFO.STEP.TOTAL_ACTIVITY_COST : {
                    const.INFO.VALUE : self.GetTotalActivityCost(),
                    const.INFO.DESCRIPTION : "total-activity-cost of currency in current step"
                },
                const.INFO.STEP.TOTAL_EVERAGE_AVERAGE_RATE : {
                    const.INFO.VALUE : self.GetTotalEverageActivityRate(),
                    const.INFO.DESCRIPTION : "total-everage-activity-rate for total-cost at the in current step"
                },
                const.INFO.STEP.PROFIT_EXPECTED_LEFT : {
                    const.INFO.VALUE : self.GetProfitLeft(),
                    const.INFO.DESCRIPTION : "total-profit for left currency for the strategy"
                },
                const.INFO.STEP.PROFIT_EXPECTED_RIGHT : {
                    const.INFO.VALUE : self.GetProfitRight(),
                    const.INFO.DESCRIPTION : "total-profit for left currency for the strategy"
                },
                const.INFO.STEP.SELL_RATE : {
                    const.INFO.VALUE : self.GetSellRate(),
                    const.INFO.DESCRIPTION : "step-sell-rate of currency in current step"
                },
                const.INFO.STEP.SELL_COST : {
                    const.INFO.VALUE : self.GetSellCost(),
                    const.INFO.DESCRIPTION : "step-sell-cost of currency in current step"
                },
                const.INFO.STEP.SELL_QUANTITY : {
                    const.INFO.VALUE : self.GetSellQuantity(),
                    const.INFO.DESCRIPTION : "step-sell-quantity of currency in current step"
                },
                const.INFO.STEP.BUY_RATE : {
                    const.INFO.VALUE : self.GetBuyRate(),
                    const.INFO.DESCRIPTION : "step-buy-rate of currency in current step"
                },
                const.INFO.STEP.BUY_COST : {
                    const.INFO.VALUE : self.GetBuyCost(),
                    const.INFO.DESCRIPTION : "step-buy-cost of currency in current step"
                },
                const.INFO.STEP.BUY_QUANTITY : {
                    const.INFO.VALUE : self.GetBuyQuantity(),
                    const.INFO.DESCRIPTION : "step-buy-quantity of currency in current step"
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
        self._InitializeNextStep()
        return self._next_step

    # brief: compute the specified-step regarding current trade-strategy
    # param: to_step - target trade-step
    # return: deep copy of the current trade-strategy presented on the specified-step
    def ComputeToStep(self, to_step):
        if self._is_initialized:
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
        commission_cost = sell_cost / sell_commission
        return commission_cost / sell_quantity

    # brief: compute sell-rate of strategy-trade for current strategy-step for desired profit
    # param: buy_quantity - desired quantity of buy-currency
    # param: buy_cost - target cost of buy
    # return: trade-rate for sell
    def ComputeBuyRate(self, buy_quantity, buy_cost):
        buy_commission = self._parameters[const.PARAMS.GLOBAL_BUY_COMMISSION]
        commission_quantity = buy_quantity / buy_commission
        return buy_cost / commission_quantity

    # NOTE: Create...

    # brief: gets string from which is possible restore trade-strategy to current state
    # return: trade-strategy restore string
    def CreateRecoveryString(self):
        if self._is_initialized:
            return json.dumps(self._CreateRecoveryParameters(), indent=4)
        raise error.NotInitializedStrategy()

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
        return const.ID.StairsBase
