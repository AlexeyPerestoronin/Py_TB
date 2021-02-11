import math
import copy
import decimal

_d = decimal.Decimal

from strategy.stairs import Dependency, CostComputedS
import strategy.const as const

# note1: DD - difficult dependent
class CostComputedDD(CostComputedS, Dependency):
    def __init__(self):
        CostComputedS.__init__(self)
        Dependency.__init__(self)
        self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_2] = None

    def _GetNextSellRate(self):
        base_rate = None
        coefficient2 = self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_2]
        if self._previous_step:
            base_rate = self._previous_step._parameters[const.PARAMS.STEP_BUY_RATE]
        else:
            base_rate = self._parameters[const.PARAMS.INIT_RATE]
        base_rate -= coefficient2
        return base_rate

    def SetCoefficient2(self, coefficient2):
        self._parameters[const.PARAMS.GLOBAL_COEFFICIENT_2] = _d(coefficient2)

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.COST_COMPUTED_D