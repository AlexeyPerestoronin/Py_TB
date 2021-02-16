import os
import sys
import unittest

sys.path.insert(0, os.getcwd())

import common
import common.faf as faf

import strategy.const as const

from strategy.stairs.__test_Strairs__ import SrairsStandartTest
from strategy.stairs.sell_and_buy.rate_computed import SbRcSimple

class Test4(SrairsStandartTest):
    def setUp(self):
        SrairsStandartTest.setUp(self)
        self._stairs = SbRcSimple()
        self._stairs.SetAvailableCurrency("60000")
        self._stairs.SetCommissionBuy("0.996")
        self._stairs.SetCommissionSell("0.996")
        self._stairs.SetCoefficient1("1.5")
        self._stairs.SetCostPrecision("4")
        self._stairs.SetRatePrecision("4")
        self._stairs.SetQuantityPrecision("8")
        self._stairs.SetProfit("1.01")
        self._stairs.SetInitRate("0.012")
        self._stairs.SetInitQuantity("5000")
        self._stairs.Init()

    # brief: testing identification of strategy-id
    def test1(self):
        self.assertEqual(SbRcSimple.GetID(), const.ID.SbRcSimple)

    # brief: testing a creation of strategy preview
    def test2(self):
        save_strategy_filepath = os.path.join(faf.SplitPath1(__file__), "SbRcSimple.log")
        self.PrepareStrategyPreview(save_strategy_filepath)

    # brief: testing saving and restoring from string
    def test3(self):
        self.SaveAndRestoreFromString()

    # brief: testing saving and restoring from file
    def test4(self):
        self.SaveAndRestoreFromFile()

if __name__ == "__main__":
    unittest.main()
