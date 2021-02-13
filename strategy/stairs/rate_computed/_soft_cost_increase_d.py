import strategy.const as const
import strategy.stairs.rate_computed as ss_rc

class RCSoftCostIncreaseD(ss_rc.RCDependency):
    def __init__(self):
        ss_rc.RCDependency.__init__(self)

    def _ComputeBuyCost(self):
        current_step_buy_cost = None
        first_step_buy_cost = self._first_step._parameters[const.PARAMS.INIT_COST]
        if self._previous_step:
            previous_step_buy_cost = self._previous_step._parameters[const.PARAMS.STEP_BUY_COST]
            current_step_buy_cost = previous_step_buy_cost + first_step_buy_cost
        else:
            current_step_buy_cost = first_step_buy_cost
        self._parameters[const.PARAMS.STEP_BUY_COST] = current_step_buy_cost

    @classmethod
    def GetID(cls):
        return const.ID.RCSoftCostIncreaseD
