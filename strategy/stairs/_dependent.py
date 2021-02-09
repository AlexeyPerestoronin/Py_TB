import math
import copy

from strategy.stairs import Simple
import strategy.const as const

class Dependency(Simple):
    def __init__(self):
        Simple.__init__(self)

    # brief: gets sell-rate for next-step
    # return: the sell-rate for next-step
    def _GetNextSellRate(self):
        if self._previous_step:
            return self._previous_step._parameters[const.PARAMS.STEP_BUY_RATE]
        else:
            return self._parameters[const.PARAMS.INIT_RATE]

    # brief: compute buy-cost for current strategy-step to buy-action
    def _ComputeBuyCost(self):
        if self._previous_step:
            self._parameters[const.PARAMS.STEP_BUY_COST] = self._previous_step._parameters[const.PARAMS.STEP_BUY_COST] * self._parameters[const.PARAMS.STEP_COEFFICIENT_1]
        else:
            self._parameters[const.PARAMS.STEP_BUY_COST] = self._parameters[const.PARAMS.INIT_COST] * self._parameters[const.PARAMS.STEP_COEFFICIENT_1]

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.DEPENDENT
