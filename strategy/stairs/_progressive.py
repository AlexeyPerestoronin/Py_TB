import math
import copy

from strategy.stairs import Dependency
import strategy.const as const

class Progressive(Dependency):
    def __init__(self):
        Dependency.__init__(self)

    # brief: gets next coefficient
    # return: next coefficient
    def _GetNextCoefficient(self):
        step_coefficient = self._coefficient
        for _ in range(1, self._step):
            step_coefficient *= 0.9
        if step_coefficient < 1.0:
            step_coefficient = 1.0
        return step_coefficient

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.STAIRS_PROGRESSIVE