import os
import sys
import unittest

sys.path.insert(0, os.getcwd())

import common
import common.faf as faf
import common.log as log
import common.algorithms as alg

import strategy.const as const

from strategy.stairs.__test_Strairs__ import Test_Srairs
from strategy.stairs import ProgressiveD

class StandartStrategy:
    def __init__ (self):
        self._stairs = ProgressiveD()
        self._stairs.SetAvailableCurrency(100000)
        self._stairs.SetCommissionBuy(0.998)
        self._stairs.SetCommissionSell(0.9994)
        self._stairs.SetCoefficient(3)
        self._stairs.SetPricePrecision1(3)
        self._stairs.SetQuantityPrecision1(8)
        self._stairs.SetProfit(1.01)
        self._stairs.Init(67.51, 500)

class Test1_StairsProgressiveD(unittest.TestCase):
    def test_GetID(self):
        self.assertEqual(ProgressiveD.GetID(), const.ID.STAIRS_PROGRESSIVE_D)

class Test2_StairsProgressiveD(unittest.TestCase, StandartStrategy):
    def setUp(self):
        StandartStrategy.__init__(self)

    def test_SaveAndRestore_from_string(self):
        self._stairs = self._stairs.ComputeToStep(3)
        self._stairs = self._stairs.ComputeToStep(2)
        recovery_string = self._stairs.CreateRecoveryString()
        restore_stairs = ProgressiveD.RestoreFromRecoveryString(recovery_string)
        self.assertTrue(self._stairs.GetStep(), restore_stairs.GetStep())
        self.assertTrue(self._stairs.GetBuyRate(), restore_stairs.GetBuyRate())
        self.assertTrue(self._stairs.GetSellRate(), restore_stairs.GetSellRate())
        self.assertTrue(self._stairs.GetInfo(), restore_stairs.GetInfo())

class Test3_StairsProgressiveD(unittest.TestCase, StandartStrategy):
    def setUp(self):
        StandartStrategy.__init__(self)
        self._save_filepath = os.path.join(faf.SplitPath1(sys.argv[0]), "stairs-ProgressiveD.save_file.log")

    def test_SaveAndRestore_from_file(self):
        filepath = os.path.join(faf.SplitPath1(sys.argv[0]), self._save_filepath)
        self._stairs = self._stairs.ComputeToStep(3)
        self._stairs = self._stairs.ComputeToStep(2)
        self._stairs.SaveToFile(filepath)
        restore_stairs = ProgressiveD.RestoreFromFile(filepath)
        self.assertTrue(self._stairs.GetStep(), restore_stairs.GetStep())
        self.assertTrue(self._stairs.GetBuyRate(), restore_stairs.GetBuyRate())
        self.assertTrue(self._stairs.GetSellRate(), restore_stairs.GetSellRate())
        self.assertTrue(self._stairs.GetInfo(), restore_stairs.GetInfo())

    def tearDown(self):
        faf.DeleteFile1(self._save_filepath)

class Test4_StairsProgressiveD(unittest.TestCase, Test_Srairs):
    def setUp(self):
        Test_Srairs.__init__(self, ProgressiveD(), "StairsProgressiveD-BTC_USD.log")
        self._stairs.SetAvailableCurrency(1000)
        self._stairs.SetCommissionBuy(0.998)
        self._stairs.SetCommissionSell(0.9994)
        self._stairs.SetCoefficient(3)
        self._stairs.SetPricePrecision1(3)
        self._stairs.SetQuantityPrecision1(8)
        self._stairs.SetProfit(1.01)
        self._stairs.Init(19000, 10)

class Test5_StairsProgressiveD(unittest.TestCase, Test_Srairs):
    def setUp(self):
        Test_Srairs.__init__(self, ProgressiveD(), "StairsProgressiveD-ETH_USDT.log")
        self._stairs.SetAvailableCurrency(1400)
        self._stairs.SetCommissionBuy(1)
        self._stairs.SetCommissionSell(1)
        self._stairs.SetCoefficient(3)
        self._stairs.SetPricePrecision1(4)
        self._stairs.SetQuantityPrecision1(8)
        self._stairs.SetProfit(1.01)
        self._stairs.Init(1400, 10)

if __name__ == "__main__":
    unittest.main()
