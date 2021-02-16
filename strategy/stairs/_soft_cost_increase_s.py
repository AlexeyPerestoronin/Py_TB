from strategy.stairs import Simple
import strategy.const as const

class SoftCostIncreaseS(Simple):
    def __init__(self):
        Simple.__init__(self)

    # brief: compute buy-cost for current strategy-step to buy-action
    def _ComputeBuyCost(self):
        if self._previous_step:
            self._parameters[const.PARAMS.STEP_BUY_COST] = self._previous_step._parameters[const.PARAMS.STEP_BUY_COST] + self._first_step._parameters[const.PARAMS.INIT_COST]
        else:
            self._parameters[const.PARAMS.STEP_BUY_COST] = self._first_step._parameters[const.PARAMS.INIT_COST]

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.SOFT_COST_INCREASE_S