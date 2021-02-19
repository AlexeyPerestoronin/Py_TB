import trader.completed_policy as trader_cp
import trader.completed_policy.consts as const

class InfinityCP(trader_cp.BaseCS):
    def __init__(self):
        trader_cp.BaseCS.__init__(self)

    def SetAllParametersFromDict(self, params):
        pass

    def Init(self):
        pass

    def Check(self):
        return True

    @classmethod
    def GetID(cls):
        return const.IDs.INFINITY_CP.Key
