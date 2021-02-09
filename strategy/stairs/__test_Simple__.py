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
from strategy.stairs import Simple

class StandartStrategy(unittest.TestCase):
    def setUp(self):
        self._stairs = Simple()
        self._stairs.SetAvailableCurrency(200000)
        self._stairs.SetCommissionBuy(0.996)
        self._stairs.SetCommissionSell(0.996)
        self._stairs.SetCoefficient1(2)
        self._stairs.SetPricePrecision(4)
        self._stairs.SetQuantityPrecision(8)
        self._stairs.SetProfit(1.003)
        self._stairs.Init(1400, 100)

    def CompareTwoStrategy(self, strategy_1, strategy_2):
        self.assertTrue(strategy_1.IsInitialized())
        self.assertTrue(strategy_2.IsInitialized())
        self.assertEqual(strategy_1.GetStep(), strategy_2.GetStep())
        self.assertEqual(strategy_1.GetSellRate(), strategy_2.GetSellRate())
        self.assertEqual(strategy_1.GetSellCost(), strategy_2.GetSellCost())
        self.assertEqual(strategy_1.GetSellQuantity(), strategy_2.GetSellQuantity())
        self.assertEqual(strategy_1.GetSellProfit(), strategy_2.GetSellProfit())
        self.assertEqual(strategy_1.GetBuyRate(), strategy_2.GetBuyRate())
        self.assertEqual(strategy_1.GetBuyCost(), strategy_2.GetBuyCost())
        self.assertEqual(strategy_1.GetBuyQuantity(), strategy_2.GetBuyQuantity())
        self.assertEqual(strategy_1.GetTotalBuyCost(), strategy_2.GetTotalBuyCost())
        self.assertEqual(strategy_1.GetTotalEverageBuyRate(), strategy_2.GetTotalEverageBuyRate())

class Test1_ID(unittest.TestCase):
    def test_GetID(self):
        self.assertEqual(Simple.GetID(), const.ID.SIMPLE)

class Test2_save_and_restore_from_string(StandartStrategy):
    def test1(self):
        self._stairs = self._stairs.ComputeToStep(3)
        self._stairs = self._stairs.ComputeToStep(2)
        recovery_string = self._stairs.CreateRecoveryString()
        restore_stairs = Simple.RestoreFromRecoveryString(recovery_string)
        self.CompareTwoStrategy(self._stairs, restore_stairs)

    def test2(self):
        self._stairs = self._stairs.ComputeToStep(3)
        self._stairs = self._stairs.ComputeToStep(6)
        recovery_string = self._stairs.CreateRecoveryString()
        restore_stairs = Simple.RestoreFromRecoveryString(recovery_string)
        self.CompareTwoStrategy(self._stairs, restore_stairs)
class Test3_save_and_restore_from_file(StandartStrategy):
    def setUp(self):
        StandartStrategy.setUp(self)
        self._save_filepath = os.path.join(faf.SplitPath1(sys.argv[0]), "stairs-Simple.save_file.log")

    def test1(self):
        filepath = os.path.join(faf.SplitPath1(sys.argv[0]), self._save_filepath)
        self._stairs = self._stairs.ComputeToStep(3)
        self._stairs = self._stairs.ComputeToStep(2)
        self._stairs.SaveToFile(filepath)
        restore_stairs = Simple.RestoreFromFile(filepath)
        self.CompareTwoStrategy(self._stairs, restore_stairs)

    def test2(self):
        filepath = os.path.join(faf.SplitPath1(sys.argv[0]), self._save_filepath)
        self._stairs = self._stairs.ComputeToStep(3)
        self._stairs = self._stairs.ComputeToStep(6)
        self._stairs.SaveToFile(filepath)
        restore_stairs = Simple.RestoreFromFile(filepath)
        self.CompareTwoStrategy(self._stairs, restore_stairs)

    def tearDown(self):
        faf.DeleteFile1(self._save_filepath)

class Test5_StairsSoftCostIncreaseDS2(unittest.TestCase, Test_Srairs):
    def setUp(self):
        Test_Srairs.__init__(self, Simple(), "Simple.log")
        self._stairs.SetAvailableCurrency(14000)
        self._stairs.SetCommissionBuy(1)
        self._stairs.SetCommissionSell(1)
        self._stairs.SetCoefficient1(2)
        self._stairs.SetPricePrecision(4)
        self._stairs.SetQuantityPrecision(8)
        self._stairs.SetProfit(1.003)
        self._stairs.Init(1400, 10)

if __name__ == "__main__":
    unittest.main()
