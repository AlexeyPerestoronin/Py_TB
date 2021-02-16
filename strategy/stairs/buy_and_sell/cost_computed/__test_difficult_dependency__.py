import os
import sys
import unittest

sys.path.insert(0, os.getcwd())

import common
import common.faf as faf

import strategy.const as const

from strategy.stairs.__test_Strairs__ import SrairsStandartTest
from strategy.stairs.buy_and_sell.cost_computed import BsCcDifficultDependency

class Test4(SrairsStandartTest):
    def setUp(self):
        SrairsStandartTest.setUp(self)
        self._stairs = BsCcDifficultDependency()
        self._stairs.SetAvailableCurrency("14000")
        self._stairs.SetCommissionBuy("0.996")
        self._stairs.SetCommissionSell("0.996")
        self._stairs.SetCoefficient1("60")
        self._stairs.SetCoefficient2("30")
        self._stairs.SetCostPrecision("4")
        self._stairs.SetRatePrecision("4")
        self._stairs.SetQuantityPrecision("8")
        self._stairs.SetProfit("1.003")
        self._stairs.SetInitRate("1400")
        self._stairs.SetInitCost("100")
        self._stairs.Init()

    # brief: testing identification of strategy-id
    def test1(self):
        self.assertEqual(BsCcDifficultDependency.GetID(), const.ID.BsCcDifficultDependency)

    # brief: testing a creation of strategy preview
    def test2(self):
        save_strategy_filepath = os.path.join(faf.SplitPath1(__file__), "BsCcDifficultDependency.log")
        self.PrepareStrategyPreview(save_strategy_filepath)

    # brief: testing saving and restoring from string
    def test3(self):
        self.SaveAndRestoreFromString()

    # brief: testing saving and restoring from file
    def test4(self):
        self.SaveAndRestoreFromFile()

if __name__ == "__main__":
    unittest.main()
