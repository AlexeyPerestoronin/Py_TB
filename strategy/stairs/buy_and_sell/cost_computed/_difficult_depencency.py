import strategy.const as const
import strategy.stairs.buy_and_sell.cost_computed as ss_bs_cc

class CCDifficultDependency(ss_bs_cc.CCDependency):
    def __init__(self):
        ss_bs_cc.CCDependency.__init__(self)

    def _GetNextSellRate(self):
        base_rate = None
        coefficient2 = self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_2]
        if self._previous_step:
            base_rate = self._previous_step._parameters[const.PARAMS.STEP_BUY_RATE]
        else:
            base_rate = self._parameters[const.PARAMS.INIT_RATE]
        base_rate -= coefficient2
        return base_rate

    @classmethod
    def GetID(cls):
        return const.ID.CCDifficultDependency
