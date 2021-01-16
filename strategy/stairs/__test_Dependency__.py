import os
import sys
import unittest

sys.path.insert(0, os.getcwd())

from strategy.stairs.__test_Strairs__ import Test_Srairs

import common
import common.faf as faf
import common.log as log
import common.algorithms as alg
import strategy.const as const
from strategy.stairs import Simple, Dependency

class Test_StairsDependency(unittest.TestCase, Test_Srairs):
    def setUp(self):
        Test_Srairs.__init__(self, Dependency(), "StairsDependency.log")
        self._stairs.SetAvailableCurrency(1000000)
        self._stairs.SetCommissionBuy(0.998)
        self._stairs.SetCommissionSell(0.9994)
        self._stairs.SetCoefficient(2)
        self._stairs.SetPricePrecision1(3)
        self._stairs.SetQuantityPrecision1(8)
        self._stairs.SetProfit(1.01)
        self._stairs.Init(67.51, 500)


    def test_GetID(self):
        self.assertTrue(Dependency.GetID(), const.ID.STAIRS_DEPENDENT)

    def test_SaveAndRestore(self):
        filepath = os.path.join(faf.SplitPath1(sys.argv[0]), "stairs-dependency.save_file.log")
        self._stairs = self._stairs.ComputeToStep(3)
        self._stairs = self._stairs.ComputeToStep(2)
        self._stairs.SaveToFile(filepath)
        restore_stairs = Simple.RestoreFromFile(filepath)
        self.assertTrue(self._stairs.GetStep(), restore_stairs.GetStep())
        self.assertTrue(self._stairs.GetBuyRate(), restore_stairs.GetBuyRate())
        self.assertTrue(self._stairs.GetSellRate(), restore_stairs.GetSellRate())
        self.assertTrue(self._stairs.GetInfo(), restore_stairs.GetInfo())

class Test_StairsDependency1(unittest.TestCase, Test_Srairs):
    def setUp(self):
        Test_Srairs.__init__(self, Dependency(), "StairsDependency-BTC_USD.log")
        self._stairs.SetAvailableCurrency(1500)
        self._stairs.SetCommissionBuy(0.998)
        self._stairs.SetCommissionSell(0.9994)
        self._stairs.SetCoefficient(2)
        self._stairs.SetPricePrecision1(2)
        self._stairs.SetQuantityPrecision1(8)
        self._stairs.SetProfit(1.001)
        self._stairs.Init(19000, 10)

class Test_StairsDependency2(unittest.TestCase, Test_Srairs):
    def setUp(self):
        Test_Srairs.__init__(self, Dependency(), "StairsDependency-ETH_RUB.log")
        self._stairs.SetAvailableCurrency(98000)
        self._stairs.SetCommissionBuy(0.998)
        self._stairs.SetCommissionSell(0.9994)
        self._stairs.SetCoefficient(2)
        self._stairs.SetPricePrecision1(4)
        self._stairs.SetQuantityPrecision1(8)
        self._stairs.SetProfit(1.001)
        self._stairs.Init(85000, 500)
if __name__ == "__main__":
    unittest.main()
