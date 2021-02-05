from strategy.stairs import DependencySubsteps
import strategy.const as const

class SoftCostIncreaseDS(DependencySubsteps):
    def __init__(self):
        DependencySubsteps.__init__(self)

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
        return const.ID.SOFT_COST_INCREASE_DS
