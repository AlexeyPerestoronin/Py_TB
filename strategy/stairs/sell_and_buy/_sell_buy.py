import common.precision as c_precision

import strategy.stairs as ss
import strategy.const as const
import strategy.const.errors as error

# brief: implements template for all simple stairs trade-strategy realizing sell-buy trading principle
class StairsSellBuy(ss.StairsBase):
    def __init__(self):
        ss.StairsBase.__init__(self)

    def _CollectStatistic(self):
        raise error.MethodIsNotImplemented()

    # NOTE: Get...

    def GetSellCost(self):
        raise error.MethodIsNotImplemented()

    def GetSellRate(self):
        raise error.MethodIsNotImplemented()

    def GetSellQuantity(self):
        raise error.MethodIsNotImplemented()

    def GetBuyCost(self):
        raise error.MethodIsNotImplemented()

    def GetBuyRate(self):
        raise error.MethodIsNotImplemented()

    def GetBuyQuantity(self):
        raise error.MethodIsNotImplemented()

    def GetTotalActivityCost(self):
        raise error.MethodIsNotImplemented()

    def GetTotalEverageActivityRate(self):
        raise error.MethodIsNotImplemented()

    def GetStepProfit(self):
        raise error.MethodIsNotImplemented()

    def GetProfit(self):
        raise error.MethodIsNotImplemented()

    def GetDifferenceBetweenRate(self):
        raise error.MethodIsNotImplemented()

    @classmethod
    def GetID(cls):
        return const.ID.StairsSellBuy
