import strategy.stairs.buy_and_sell.rate_computed as ss_bs_rt
import strategy.stairs.buy_and_sell.cost_computed as ss_bs_cc
import strategy.const as const

class CCDependency(ss_bs_cc.CCSimple, ss_bs_rt.RCDependency):
    def __init__(self):
        ss_bs_cc.CCSimple.__init__(self)
        ss_bs_rt.RCDependency.__init__(self)

    @classmethod
    def GetID(cls):
        return const.ID.CCDependency
