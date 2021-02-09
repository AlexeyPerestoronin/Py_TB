from strategy.stairs import Dependency
import strategy.const as const

class FixedBuyCostD(Dependency):
    def __init__(self):
        Dependency.__init__(self)

    # brief: compute buy-cost for current strategy-step to buy-action
    def _ComputeBuyCost(self):
        self._parameters[const.PARAMS.STEP_BUY_COST] = self._first_step._parameters[const.PARAMS.INIT_COST]

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.FIXED_BUY_COST_D
