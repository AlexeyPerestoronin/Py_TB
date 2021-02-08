import math
import copy

from strategy.stairs import Dependency, CostComputedS
import strategy.const as const

class CostComputedD(CostComputedS, Dependency):
    def __init__(self):
        CostComputedS.__init__(self)
        Dependency.__init__(self)

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.COST_COMPUTED_D