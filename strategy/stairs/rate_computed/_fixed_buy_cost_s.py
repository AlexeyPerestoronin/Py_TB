import strategy.const as const
import strategy.stairs.rate_computed as ss_rc

class RCFixedBuyCostS(ss_rc.RCSimple):
    def __init__(self):
        ss_rc.RCSimple.__init__(self)

    def _ComputeBuyCost(self):
        self._parameters[const.PARAMS.STEP_BUY_COST] = self._first_step._parameters[const.PARAMS.INIT_COST]

    @classmethod
    def GetID(cls):
        return const.ID.RCFixedBuyCostS
