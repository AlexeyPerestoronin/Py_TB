import strategy.stairs.rate_computed as ss_rt
import strategy.stairs.cost_computed as ss_cc
import strategy.const as const

class CCDependency(ss_cc.CCSimple, ss_rt.RCDependency):
    def __init__(self):
        ss_cc.CCSimple.__init__(self)
        ss_rt.RCDependency.__init__(self)

    @classmethod
    def GetID(cls):
        return const.ID.CCDependency
