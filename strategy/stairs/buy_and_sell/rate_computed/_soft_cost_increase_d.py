import strategy.const as const
import strategy.stairs.buy_and_sell.rate_computed as ss_bs_rc

class BsRcSoftCostIncreaseD(ss_bs_rc.BsRcDependency):
    def __init__(self):
        ss_bs_rc.BsRcDependency.__init__(self)

    def _ComputeBuyCost(self):
        current_step_buy_cost = None
        first_step_buy_cost = self._first_step._parameters[const.PARAMS.STEP_INIT_COST.Key]
        if self._previous_step:
            previous_step_buy_cost = self._previous_step._parameters[const.PARAMS.STEP_BUY_COST.Key]
            current_step_buy_cost = previous_step_buy_cost + first_step_buy_cost
        else:
            current_step_buy_cost = first_step_buy_cost
        self._parameters[const.PARAMS.STEP_BUY_COST.Key] = current_step_buy_cost

    @classmethod
    def GetID(cls):
        return const.ID.BsRcSoftCostIncreaseD
