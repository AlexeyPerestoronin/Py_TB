import strategy.const as const
import strategy.stairs.rate_computed as ss_rc

class RCFixedBuyCostD(ss_rc.RCDependency):
    def __init__(self):
        ss_rc.RCDependency.__init__(self)

    def _ComputeBuyCost(self):
        self._parameters[const.PARAMS.STEP_BUY_COST] = self._first_step._parameters[const.PARAMS.INIT_COST]

    @classmethod
    def GetID(cls):
        return const.ID.RCFixedBuyCostD
