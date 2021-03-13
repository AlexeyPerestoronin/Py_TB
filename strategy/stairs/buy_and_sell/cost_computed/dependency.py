import strategy.stairs.buy_and_sell.rate_computed as ss_bs_rt
import strategy.stairs.buy_and_sell.cost_computed as ss_bs_cc
import strategy.const as const

class BsCcDependency(ss_bs_cc.BsCcSimple, ss_bs_rt.BsRcDependency):
    def __init__(self):
        ss_bs_cc.BsCcSimple.__init__(self)
        ss_bs_rt.BsRcDependency.__init__(self)

    @classmethod
    def GetID(cls):
        return const.ID.BsCcDependency
