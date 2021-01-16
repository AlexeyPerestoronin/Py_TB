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
            return self._previous_step._buy_rate
        else:
            return self._init_rate

    # brief: compute buy-cost for current strategy-step to buy-action
    def _ComputeBuyCost(self):
        if self._previous_step:
            self._buy_cost = self._previous_step._buy_cost * self._GetNextCoefficient()
        else:
            self._buy_cost = self._init_cost * self._GetNextCoefficient()

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.STAIRS_DEPENDENT