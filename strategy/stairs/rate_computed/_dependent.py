import math
import copy

import strategy.const as const
import strategy.stairs.rate_computed as ss_rc

class RCDependency(ss_rc.RCSimple):
    def __init__(self):
        ss_rc.RCSimple.__init__(self)

    def _GetNextSellRate(self):
        if self._previous_step:
            return self._previous_step._parameters[const.PARAMS.STEP_BUY_RATE]
        else:
            return self._parameters[const.PARAMS.INIT_RATE]

    def _ComputeBuyCost(self):
        ceff1 = self._parameters[const.PARAMS.STEP_COEFFICIENT_1]
        base_cost = None
        if self._previous_step:
            base_cost = self._previous_step._parameters[const.PARAMS.STEP_BUY_COST]
        else:
            base_cost = self._parameters[const.PARAMS.INIT_COST]
        self._parameters[const.PARAMS.STEP_BUY_COST] = base_cost * ceff1

    @classmethod
    def GetID(cls):
        return const.ID.RCDependency
