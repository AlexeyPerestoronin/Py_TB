import strategy.const as const
import strategy.stairs.buy_and_sell.rate_computed as ss_bs_rc

class BsRcFixedBuyCostS(ss_bs_rc.BsRcSimple):
    def __init__(self):
        ss_bs_rc.BsRcSimple.__init__(self)

    def _ComputeBuyCost(self):
        self._parameters[const.PARAMS.STEP_BUY_COST] = self._first_step._parameters[const.PARAMS.INIT_COST]

    @classmethod
    def GetID(cls):
        return const.ID.BsRcFixedBuyCostS
