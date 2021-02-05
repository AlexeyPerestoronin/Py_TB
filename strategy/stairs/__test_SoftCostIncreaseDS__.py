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
from strategy.stairs import SoftCostIncreaseDS

class StandartStrategy:
    def __init__ (self):
        self._stairs = SoftCostIncreaseDS()
        self._stairs.SetAvailableCurrency(150000)
        self._stairs.SetCommissionBuy(0.996)
        self._stairs.SetCommissionSell(0.996)
        self._stairs.SetCoefficient(2)
        self._stairs.SetPricePrecision1(3)
        self._stairs.SetQuantityPrecision1(8)
        self._stairs.SetProfit(1.01)
        self._stairs.SetSubstepsDiffCost(500)
        self._stairs.Init(67.51, 500)

class Test1_ID(unittest.TestCase):
    def test_GetID(self):
        self.assertTrue(SoftCostIncreaseDS.GetID(), const.ID.SOFT_COST_INCREASE_DS)

class Test2_save_and_restore_from_string(unittest.TestCase, StandartStrategy):
    def setUp(self):
        StandartStrategy.__init__(self)

    def test1(self):
        self._stairs = self._stairs.ComputeToStep(3)
        self._stairs = self._stairs.ComputeToStep(2)
        recovery_string = self._stairs.CreateRecoveryString()
        restore_stairs = SoftCostIncreaseDS.RestoreFromRecoveryString(recovery_string)
        self.assertTrue(self._stairs.GetStep(), restore_stairs.GetStep())
        self.assertTrue(self._stairs.GetSubstep(), restore_stairs.GetSubstep())
        self.assertTrue(self._stairs.GetBuyRate(), restore_stairs.GetBuyRate())
        self.assertTrue(self._stairs.GetSellRate(), restore_stairs.GetSellRate())
        self.assertTrue(self._stairs.GetInfo(), restore_stairs.GetInfo())

    def test2(self):
        self._stairs = self._stairs.ComputeToStep(3)
        self._stairs = self._stairs.ComputeToStep(6)
        recovery_string = self._stairs.CreateRecoveryString()
        restore_stairs = SoftCostIncreaseDS.RestoreFromRecoveryString(recovery_string)
        self.assertTrue(self._stairs.GetStep(), restore_stairs.GetStep())
        self.assertTrue(self._stairs.GetSubstep(), restore_stairs.GetSubstep())
        self.assertTrue(self._stairs.GetBuyRate(), restore_stairs.GetBuyRate())
        self.assertTrue(self._stairs.GetSellRate(), restore_stairs.GetSellRate())
        self.assertTrue(self._stairs.GetInfo(), restore_stairs.GetInfo())

    def test3(self):
        self._stairs = self._stairs.ComputeToStep(12)
        recovery_string = self._stairs.CreateRecoveryString()
        restore_stairs = SoftCostIncreaseDS.RestoreFromRecoveryString(recovery_string)
        self.assertTrue(self._stairs.GetStep(), restore_stairs.GetStep())
        self.assertTrue(self._stairs.GetSubstep(), restore_stairs.GetSubstep())
        self.assertTrue(self._stairs.GetBuyRate(), restore_stairs.GetBuyRate())
        self.assertTrue(self._stairs.GetSellRate(), restore_stairs.GetSellRate())
        self.assertTrue(self._stairs.GetInfo(), restore_stairs.GetInfo())

class Test3_save_and_restore_from_file(unittest.TestCase, StandartStrategy):
    def setUp(self):
        StandartStrategy.__init__(self)
        self._save_filepath = os.path.join(faf.SplitPath1(sys.argv[0]), "stairs-SoftCostIncreaseDS.save_file.log")

    def test1(self):
        filepath = os.path.join(faf.SplitPath1(sys.argv[0]), self._save_filepath)
        self._stairs = self._stairs.ComputeToStep(3)
        self._stairs = self._stairs.ComputeToStep(2)
        self._stairs.SaveToFile(filepath)
        restore_stairs = SoftCostIncreaseDS.RestoreFromFile(filepath)
        self.assertTrue(self._stairs.GetStep(), restore_stairs.GetStep())
        self.assertTrue(self._stairs.GetSubstep(), restore_stairs.GetSubstep())
        self.assertTrue(self._stairs.GetBuyRate(), restore_stairs.GetBuyRate())
        self.assertTrue(self._stairs.GetSellRate(), restore_stairs.GetSellRate())
        self.assertTrue(self._stairs.GetInfo(), restore_stairs.GetInfo())

    def test2(self):
        filepath = os.path.join(faf.SplitPath1(sys.argv[0]), self._save_filepath)
        self._stairs = self._stairs.ComputeToStep(3)
        self._stairs = self._stairs.ComputeToStep(6)
        self._stairs.SaveToFile(filepath)
        restore_stairs = SoftCostIncreaseDS.RestoreFromFile(filepath)
        self.assertTrue(self._stairs.GetStep(), restore_stairs.GetStep())
        self.assertTrue(self._stairs.GetSubstep(), restore_stairs.GetSubstep())
        self.assertTrue(self._stairs.GetBuyRate(), restore_stairs.GetBuyRate())
        self.assertTrue(self._stairs.GetSellRate(), restore_stairs.GetSellRate())
        self.assertTrue(self._stairs.GetInfo(), restore_stairs.GetInfo())

    def test3(self):
        filepath = os.path.join(faf.SplitPath1(sys.argv[0]), self._save_filepath)
        self._stairs = self._stairs.ComputeToStep(10)
        self._stairs = self._stairs.ComputeToStep(6)
        self._stairs.SaveToFile(filepath)
        restore_stairs = SoftCostIncreaseDS.RestoreFromFile(filepath)
        self.assertTrue(self._stairs.GetStep(), restore_stairs.GetStep())
        self.assertTrue(self._stairs.GetSubstep(), restore_stairs.GetSubstep())
        self.assertTrue(self._stairs.GetBuyRate(), restore_stairs.GetBuyRate())
        self.assertTrue(self._stairs.GetSellRate(), restore_stairs.GetSellRate())
        self.assertTrue(self._stairs.GetInfo(), restore_stairs.GetInfo())

    def test4(self):
        filepath = os.path.join(faf.SplitPath1(sys.argv[0]), self._save_filepath)
        self._stairs = self._stairs.ComputeToStep(12)
        self._stairs.SaveToFile(filepath)
        restore_stairs = SoftCostIncreaseDS.RestoreFromFile(filepath)
        self.assertTrue(self._stairs.GetStep(), restore_stairs.GetStep())
        self.assertTrue(self._stairs.GetSubstep(), restore_stairs.GetSubstep())
        self.assertTrue(self._stairs.GetBuyRate(), restore_stairs.GetBuyRate())
        self.assertTrue(self._stairs.GetSellRate(), restore_stairs.GetSellRate())
        self.assertTrue(self._stairs.GetInfo(), restore_stairs.GetInfo())

    def tearDown(self):
        faf.DeleteFile1(self._save_filepath)

class Test5_StairsSoftCostIncreaseDS2(unittest.TestCase, Test_Srairs):
    def setUp(self):
        Test_Srairs.__init__(self, SoftCostIncreaseDS(), "SoftCostIncreaseDS.log")
        self._stairs.SetAvailableCurrency(1400)
        self._stairs.SetCommissionBuy(1)
        self._stairs.SetCommissionSell(1)
        self._stairs.SetCoefficient(2)
        self._stairs.SetPricePrecision1(4)
        self._stairs.SetQuantityPrecision1(8)
        self._stairs.SetProfit(1.003)
        self._stairs.SetSubstepsDiffCost(50)
        self._stairs.Init(1300, 100)

if __name__ == "__main__":
    unittest.main()
