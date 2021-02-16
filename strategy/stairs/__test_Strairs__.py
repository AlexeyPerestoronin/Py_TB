import os
import sys
import unittest

sys.path.insert(0, os.getcwd())

import common
import common.faf as faf
import common.log as log

import strategy
import strategy.const as const
import strategy.const.errors as error

class SrairsStandartTest(unittest.TestCase):
    def setUp(self):
        self._stairs = None

    def CompareWithStrategy(self, target_compare_strategy):
        self.assertTrue(self._stairs.IsInitialized())
        self.assertTrue(target_compare_strategy.IsInitialized())
        self.assertEqual(self._stairs.GetStep(), target_compare_strategy.GetStep())
        self.assertEqual(self._stairs.GetSellRate(), target_compare_strategy.GetSellRate())
        self.assertEqual(self._stairs.GetSellCost(), target_compare_strategy.GetSellCost())
        self.assertEqual(self._stairs.GetSellQuantity(), target_compare_strategy.GetSellQuantity())
        self.assertEqual(self._stairs.GetProfitLeft(), target_compare_strategy.GetProfitLeft())
        self.assertEqual(self._stairs.GetProfitRight(), target_compare_strategy.GetProfitRight())
        self.assertEqual(self._stairs.GetBuyRate(), target_compare_strategy.GetBuyRate())
        self.assertEqual(self._stairs.GetBuyCost(), target_compare_strategy.GetBuyCost())
        self.assertEqual(self._stairs.GetBuyQuantity(), target_compare_strategy.GetBuyQuantity())
        self.assertEqual(self._stairs.GetTotalActivityCost(), target_compare_strategy.GetTotalActivityCost())
        self.assertEqual(self._stairs.GetTotalEverageActivityRate(), target_compare_strategy.GetTotalEverageActivityRate())

    def SaveAndRestoreFromString(self, step_1=1, step_2=2):
        self._stairs = self._stairs.ComputeToStep(step_1)
        self._stairs = self._stairs.ComputeToStep(step_2)
        recovery_string = self._stairs.CreateRecoveryString()
        self.CompareWithStrategy(type(self._stairs).RestoreFromRecoveryString(recovery_string))

    def SaveAndRestoreFromFile(self, step_1=2, step_2=1):
        save_filepath = os.path.join(faf.SplitPath1(sys.argv[0]), "stairs_recovery_string.txt")
        self._stairs = self._stairs.ComputeToStep(step_1)
        self._stairs = self._stairs.ComputeToStep(step_2)
        self._stairs.SaveToFile(save_filepath)
        self.CompareWithStrategy(type(self._stairs).RestoreFromFile(save_filepath))

    def PrepareStrategyPreview(self, save_filepath):
        if self._stairs.IsInitialized():
            strategy.StrategyPreview(self._stairs).SavePreviewInFile(save_filepath)
