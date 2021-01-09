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
        next_sell_rate = None
        if self._previous_step:
            next_sell_rate = self._previous_step._buy_rate
        else:
            next_sell_rate = self._init_rate
        return next_sell_rate

    # brief: gets buy-cost for next step
    # return: the buy-cost for next-step
    def GetBuyCost(self):
        next_buy_cost = None
        if self._previous_step:
            next_buy_cost = self._previous_step._buy_cost * self._coefficient
        else:
            next_buy_cost = self._init_cost * self._coefficient
        return next_buy_cost

    # brief: get strategy-ID
    # return: strategy-ID
    @staticmethod
    def GetID():
        return const.ID.STAIRS_DEPENDENT
