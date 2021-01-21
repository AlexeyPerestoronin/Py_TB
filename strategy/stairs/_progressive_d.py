import math
import copy

from strategy.stairs import Dependency
import strategy.const as const

class ProgressiveD(Dependency):
    def __init__(self):
        Dependency.__init__(self)

    # brief: gets next coefficient
    # return: next coefficient
    def _ComputeNextCoefficient(self):
        if self._previous_step:
            self._step_coefficient = self._previous_step._step_coefficient - 0.5
        else:
            self._step_coefficient = self._init_coefficient
        if self._step_coefficient < 1.5:
            self._step_coefficient = 1.5

    # brief: get strategy-ID
    # return: strategy-ID
    @classmethod
    def GetID(cls):
        return const.ID.STAIRS_PROGRESSIVE_D