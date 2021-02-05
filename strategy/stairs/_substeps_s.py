import math
import copy

import strategy.stairs as ss
import strategy.const as const
import strategy.const.errors as error

class SimpleSubsteps(ss.Simple):
    def __init__(self):
        ss.Simple.__init__(self)
        self._diff_rate = None
        self._diff_cost = None
        self._first_substep = None
        self._substeps_total = None
        self._substep_current = None
        # buy(s)
        self._substep_buy_cost = None
        self._substep_buy_rate = None
        self._substep_buy_quantity = None
        # buy(s)
        self._substep_sell_cost = None
        self._substep_sell_rate = None
        self._substep_sell_profit = None
        self._substep_sell_quantity = None

    # brief: creates dictionary with recovery parameters by which is possible restore trade-strategy to current state
    # return: recovery dictionary
    def _CreateRecoveryParameters(self):
        recovery_params = ss.Simple._CreateRecoveryParameters(self)
        recovery_params[const.INFO.STEP.SUBINFO.SUBSTEP] = self._substep_current
        recovery_params[const.INFO.STEP.SUBINFO.DIFF_RATE] = self._diff_rate
        recovery_params[const.INFO.STEP.SUBINFO.DIFF_COST] = self._diff_cost
        return recovery_params

    # brief: restores trade-strategy state by recovery parameters
    # note1: the recovery parameters must be creates by cls._CreateRecoveryParameters function
    # param: recovery_params - target recovery parameters
    # return: restored trade-strategy
    @classmethod
    def _RestoreFromRecoveryParameters(cls, recovery_params):
        restored_strategy = cls()
        # restore (1): restore base-parameters
        restored_strategy.SetAvailableCurrency(recovery_params[const.INFO.STEP.AVAILABLE_CURRENCY])
        restored_strategy.SetPricePrecision1(recovery_params[const.INFO.GLOBAL.PRICE_PRECISION])
        restored_strategy.SetQuantityPrecision1(recovery_params[const.INFO.GLOBAL.QUANTITY_PRECISION])
        restored_strategy.SetCoefficient(recovery_params[const.INFO.GLOBAL.COEFFICIENT])
        restored_strategy.SetCommissionBuy(recovery_params[const.INFO.GLOBAL.BUY_COMMISSION])
        restored_strategy.SetCommissionSell(recovery_params[const.INFO.GLOBAL.SELL_COMMISSION])
        restored_strategy.SetProfit(recovery_params[const.INFO.GLOBAL.PROFIT])
        # restore (1): restore substep-parameters
        restored_strategy.SetSubstepsDiffCost(recovery_params[const.INFO.STEP.SUBINFO.DIFF_COST])
        # restore (2): restore base step(s)
        restored_strategy.Init(recovery_params[const.INFO.STEP.AVERAGE_RATE], recovery_params[const.INFO.STEP.TOTAL_BUY_COST])
        for _ in range(1, recovery_params[repr(const.INFO.STEP)]):
            restored_strategy = restored_strategy.ComputeNextFullStep()
        # restore (3): restore sub step(s)
        for _ in range(1, recovery_params[const.INFO.STEP.SUBINFO.SUBSTEP]):
            restored_strategy = restored_strategy.ComputeNextStep()
        return restored_strategy

    def _ComputeSubstepsTotal(self):
        substeps_total = int(self._buy_cost / self._diff_cost)
        if substeps_total < 1:
            substeps_total = 1
        self._substeps_total = substeps_total

    def _ComputeDiffRate(self):
        previous_buy_rate = None
        if self._previous_step:
            previous_buy_rate = self._previous_step._buy_rate
        else:
            previous_buy_rate = self._init_rate
        self._diff_rate = (previous_buy_rate - self._buy_rate) / self._substeps_total

    # brief: compute sell-cost for current strategy-step to sell-action
    def _ComputeSellSubstepCost(self):
        self._substep_sell_cost = self._PPD(self._substep_sell_quantity * self._substep_sell_rate)

    # brief: compute sell-profit for current strategy-step to sell-action
    def _ComputeSellSubstepProfit(self):
        additional_substep_cost = self._substep_buy_cost * (self._substep_current - 1)
        self._substep_sell_profit = self._substep_sell_cost - self._init_cost - additional_substep_cost

    # brief: compute sell-rate for current strategy-step to sell-action
    def _ComputeSellSubstepRate(self):
        additional_substep_cost = self._substep_buy_cost * (self._substep_current - 1)
        self._substep_sell_rate = self.ComputeSellRate(self._substep_sell_quantity, (self._init_cost + additional_substep_cost) * self._profit)

    # brief: compute sell-quantity for current-strategy-step to sell-action
    def _ComputeSellSubstepQuantity(self):
        additional_substep_quantity = 0
        local_previous_step = self._previous_step
        for _ in range(1, self._substep_current):
            additional_substep_quantity += local_previous_step._substep_buy_quantity * self._buy_commission
            local_previous_step = local_previous_step._previous_step
        self._substep_sell_quantity = self._QPD(self._sell_quantity + additional_substep_quantity)

    # brief: compute buy-cost for current strategy-step to buy-action
    def _ComputeBuySubstepCost(self):
        self._substep_buy_cost = self._buy_cost / self._substeps_total

    # brief: compute buy-rate for current strategy-step to buy-action
    def _ComputeBuySubstepRate(self):
        previous_buy_rate = None
        if self._previous_step:
            if self._substep_buy_rate:
                previous_buy_rate = self._substep_buy_rate
            else:
                previous_buy_rate = self._previous_step._buy_rate
        else:
            previous_buy_rate = self._init_rate
        self._substep_buy_rate = self._PPD(previous_buy_rate - self._diff_rate)

    # brief: compute buy-quantity for current strategy-step to buy-action
    def _ComputeBuySubstepQuantity(self):
        self._substep_buy_quantity =  self._QPD(self._substep_buy_cost / self._substep_buy_rate)

    # brief: compute current strategy-substep
    def _ComputeCurrentSubstep(self):
        # (buy) sequence of calculations
        self._ComputeBuySubstepCost()
        self._ComputeBuySubstepRate()
        self._ComputeBuySubstepQuantity()
        # (sell) sequence of calculations
        self._ComputeSellSubstepQuantity()
        self._ComputeSellSubstepRate()
        self._ComputeSellSubstepCost()
        self._ComputeSellSubstepProfit()

    # brief: sets quantity of substeps for all steps in trade-strategy
    # param: substeps_total_quantity - target quantity of substeps
    def SetSubstepsDiffCost(self, diff_cost):
        self._diff_cost = diff_cost

    # brief: strategy initialization
    # note1: this function must be called only after call of SetCoefficient, SetCommission and SetProfit functions
    # param: rate - currency rate on first-step
    # param: cost - currency cost on first-step
    def Init(self, rate, cost):
        ss.Simple.Init(self, rate, cost)
        self._substep_current = 1
        self._ComputeSubstepsTotal()
        self._ComputeDiffRate()
        self._ComputeCurrentSubstep()
        self._first_substep = self


    # brief: compute the next-step regarding current trade-strategy
    # return: deep copy of the current trade-strategy presented on the next-step
    def ComputeNextStep(self):
        if self._substep_current < self._substeps_total:
            self._next_step = copy.deepcopy(self)
            self._next_step._previous_step = self
            self._next_step._first_substep = self._first_substep
            self._next_step._substep_current += 1
            self._next_step._ComputeCurrentSubstep()
        else:
            # migrate settings(1): base
            self._next_step = type(self)()
            self._next_step._previous_step = self
            self._next_step.SetAvailableCurrency(self._current_available_currency)
            self._next_step.SetQuantityPrecision2(self._quantity_precision)
            self._next_step.SetPricePrecision2(self._price_precision)
            self._next_step.SetCommissionSell(self._sell_commission)
            self._next_step.SetCommissionBuy(self._buy_commission)
            self._next_step.SetCoefficient(self._init_coefficient)
            self._next_step.SetProfit(self._profit)
            # migrate settings(2): substeps settings
            self._next_step.SetSubstepsDiffCost(self._diff_cost)
            # compute cost and rate for next step (as if it is cost and rate for first step)
            cost = self._init_cost + self._buy_cost
            rate = (math.pow(self._buy_commission, 2) * self._GetNextSellRate()) / self._profit
            self._next_step._first_step = self._first_step
            self._next_step.Init(rate, cost)
        return self._next_step

    def ComputeNextFullStep(self):
        copy_first_substep = copy.deepcopy(self._first_substep)
        for _ in range (0, self._substeps_total):
            copy_first_substep = copy_first_substep.ComputeNextStep()
        return copy_first_substep

    def GetSubstep(self):
        return self._substep_current

    # brief: gets sell-cost for current step
    # return: the sell-cost for current step
    def GetSellCost(self):
        return self._substep_sell_cost

    # brief: gets sell-rate for current step
    # return: the sell-rate for current step
    def GetSellRate(self):
        return self._substep_sell_rate

    # brief: gets quantity for sell-order for current step
    # return: the quantity for sell-order for current step
    def GetSellQuantity(self):
        return self._substep_sell_quantity

    # brief: gets profit for sell-order for current step
    # return: the profit for sell-order for current step
    def GetSellProfit(self):
        return self._substep_sell_profit

    # brief: gets buy-cost for current step
    # return: the buy-cost for current step
    def GetBuyCost(self):
        return self._substep_buy_cost

    # brief: gets buy-rate for current step
    # return: the buy-rate for current step
    def GetBuyRate(self):
        return self._substep_buy_rate

    # brief: gets buy-quantity for current step
    # return: the buy-quantity for current step
    def GetBuyQuantity(self):
        return self._substep_buy_quantity

    def GetSubstepInfo(self):
        substep_info = {
            const.INFO.STEP.SUBINFO.DIFF_RATE : {
                const.INFO.VALUE : self._diff_rate,
                const.INFO.DESCRIPTION : "difference between two substeps' rate"
            },
            const.INFO.STEP.SUBINFO.DIFF_COST : {
                const.INFO.VALUE : self._diff_cost,
                const.INFO.DESCRIPTION : "difference between two substeps' cost"
            },
            const.INFO.STEP.SUBINFO.SUBRATE_SELL_COST : {
                const.INFO.VALUE : self._substep_sell_cost,
                const.INFO.DESCRIPTION : "sell-cost for current substep"
            },
            const.INFO.STEP.SUBINFO.SUBRATE_SELL_RATE : {
                const.INFO.VALUE : self._substep_sell_rate,
                const.INFO.DESCRIPTION : "sell-rate for current substep"
            },
            const.INFO.STEP.SUBINFO.SUBRATE_SELL_PROFIT : {
                const.INFO.VALUE : self._substep_sell_profit,
                const.INFO.DESCRIPTION : "sell-profit for current substep"
            },
            const.INFO.STEP.SUBINFO.SUBRATE_SELL_QUANTITY : {
                const.INFO.VALUE : self._substep_sell_quantity,
                const.INFO.DESCRIPTION : "sell-quantity for current substep"
            },
            const.INFO.STEP.SUBINFO.SUBRATE_BUY_COST : {
                const.INFO.VALUE : self._substep_buy_cost,
                const.INFO.DESCRIPTION : "buy-cost for current substep"
            },
            const.INFO.STEP.SUBINFO.SUBRATE_BUY_RATE : {
                const.INFO.VALUE : self._substep_buy_rate,
                const.INFO.DESCRIPTION : "buy-rate for current substep"
            },
            const.INFO.STEP.SUBINFO.SUBRATE_BUY_QUANTITY : {
                const.INFO.VALUE : self._substep_buy_quantity,
                const.INFO.DESCRIPTION : "buy-quantity for current substep"
            },
        }
        return substep_info

    def GetInfo(self):
        info = ss.Simple.GetInfo(self)
        copy_first_substep = copy.deepcopy(self._first_substep)
        substeps_info = [copy_first_substep.GetSubstepInfo()]
        for _ in range (1, self._substeps_total):
            copy_first_substep = copy_first_substep.ComputeNextStep()
            substeps_info.append(copy_first_substep.GetSubstepInfo())
        info[const.INFO.STEP][const.INFO.STEP.SUBINFO] = substeps_info
        return info

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.SIMPLE_SUBSTEPS
