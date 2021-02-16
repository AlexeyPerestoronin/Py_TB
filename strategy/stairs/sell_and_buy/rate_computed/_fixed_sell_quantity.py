import math
import copy
import json
import decimal

import common.faf as faf
import common.precision as c_precision

import strategy.const as const
import strategy.const.errors as error
import strategy.stairs.sell_and_buy.rate_computed as ss_sb_rc

class SbRcFixedSellQuantityS(ss_sb_rc.SbRcSimple):
    def __init__(self):
        ss_sb_rc.SbRcSimple.__init__(self)

    def _ComputeSellQuantity(self):
        first_step_sell_quantity = self._first_step._parameters[const.PARAMS.INIT_QUANTITY]
        self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY] -= first_step_sell_quantity
        if self._parameters[const.PARAMS.STEP_AVAILABLE_CURRENCY] < 0.:
            raising_error = error.ExceededAvailableCurrency()
            raising_error.SetBuyQuantity(self._QP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_QUANTITY]))
            raising_error.SetBuyCost(self._CP.DownDecimal(self._parameters[const.PARAMS.STEP_BUY_COST]))
            raising_error.SetBuyRate(self._RP.UpDecimal(self._parameters[const.PARAMS.STEP_BUY_RATE]))
            raise raising_error
        self._parameters[const.PARAMS.STEP_SELL_QUANTITY] = first_step_sell_quantity

    @classmethod
    def GetID(cls):
        return const.ID.SbRcFixedSellQuantityS
