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
        self._stairs.SetCommission(1.0)
        self._stairs.SetCoefficient(1.5)
        self._stairs.SetPricePrecision1(4)
        self._stairs.SetVolumePrecision1(8)
        self._stairs.SetProfit(1.001)
        self._stairs.Init(1230, 10)


    def test_GetID(self):
        self.assertTrue(Dependency.GetID(), const.ID.STAIRS_DEPENDENT)

    def test_SaveAndRestore(self):
        filepath = os.path.join(faf.SplitPath1(sys.argv[0]), "stairs-dependency.save_file.log")
        self._stairs = self._stairs.ComputeToStep(10)
        self._stairs = self._stairs.ComputeToStep(5)
        self._stairs.SaveToFile(filepath)
        restore_stairs = Simple.RestoreFromFile(filepath)
        self.assertTrue(self._stairs.GetStep(), restore_stairs.GetStep())
        self.assertTrue(self._stairs.GetBuyRate(), restore_stairs.GetBuyRate())
        self.assertTrue(self._stairs.GetSellRate(), restore_stairs.GetSellRate())
        self.assertTrue(self._stairs.GetInfo(), restore_stairs.GetInfo())

class Test_StairsDependency1(unittest.TestCase, Test_Srairs):
    def setUp(self):
        Test_Srairs.__init__(self, Dependency(), "StairsDependency-BTC_USD.log")
        self._stairs.SetCommission(0.996)
        self._stairs.SetCoefficient(2)
        self._stairs.SetPricePrecision1(3)
        self._stairs.SetVolumePrecision1(8)
        self._stairs.SetProfit(1.01)
        self._stairs.Init(19000, 10)

class Test_StairsDependency2(unittest.TestCase, Test_Srairs):
    def setUp(self):
        Test_Srairs.__init__(self, Dependency(), "StairsDependency-EXMO_USDT.log")
        self._stairs.SetCommission(1.0)
        self._stairs.SetCoefficient(2)
        self._stairs.SetPricePrecision1(8)
        self._stairs.SetVolumePrecision1(8)
        self._stairs.SetProfit(1.01)
        self._stairs.Init(0.00341077, 10)

if __name__ == "__main__":
    unittest.main()
