import math
import copy

from strategy.stairs import Simple
import strategy.const as const

class FixedBuyCostS(Simple):
    def __init__(self):
        Simple.__init__(self)

    # brief: compute buy-cost for current strategy-step to buy-action
    def _ComputeBuyCost(self):
        self._buy_cost = self._first_step._init_cost

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.FIXED_BUY_COST_S
