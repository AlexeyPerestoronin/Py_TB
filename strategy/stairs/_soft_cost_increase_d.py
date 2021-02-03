from strategy.stairs import Dependency
import strategy.const as const

class SoftCostIncreaseD(Dependency):
    def __init__(self):
        Dependency.__init__(self)

    # brief: compute buy-cost for current strategy-step to buy-action
    def _ComputeBuyCost(self):
        if self._previous_step:
            self._buy_cost = self._previous_step._buy_cost + self._first_step._init_cost
        else:
            self._buy_cost = self._first_step._init_cost

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.SOFT_COST_INCREASE_D