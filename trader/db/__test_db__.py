import os
import re
import sys
import time
import shutil
import unittest

sys.path.insert(0, os.getcwd())

import common.faf as faf
import trader.db as db
import trader.const as const
import trader.const.errors as errors

import strategy.stairs as ss

class DB_Test1(unittest.TestCase):
    _db_filepath = os.path.join(faf.SplitPath1(sys.argv[0]), "test_db1.sqlite")

    def setUp(self):
        self._db = db.Simple()

    def test_Connection(self):
        try:
            self._db.Init(self._db_filepath)
        except errors.NotAvailableTrading:
            pass

    @classmethod
    def tearDownClass(cls):
        faf.DeleteFile1(cls._db_filepath)

class DB_Test2(unittest.TestCase):
    _db_filepath = os.path.join(faf.SplitPath1(sys.argv[0]), "test_db2.sqlite")

    def setUp(self):
        self._init_order_id = "123456789"
        self._db = db.Simple()

    def test1_InitNewTrading(self):
        try:
            self._db.Init(self._db_filepath)
        except errors.NotAvailableTrading:
            self._db.InitNewTrading(self._init_order_id)
        self.assertEqual(self._db.GetInitialOrderId(), self._init_order_id)
        self.assertFalse(self._db.IsComplete())
        self.assertFalse(self._db.IsTrade())
        self.assertTrue(self._db.IsInit())

    def test2_Init(self):
        self._db.Init(self._db_filepath)
        self.assertEqual(self._db.GetInitialOrderId(), self._init_order_id)
        self.assertFalse(self._db.IsComplete())
        self.assertFalse(self._db.IsTrade())
        self.assertTrue(self._db.IsInit())

    @classmethod
    def tearDownClass(cls):
        faf.DeleteFile1(cls._db_filepath)

class DB_Test3(unittest.TestCase):
    _db_filepath = os.path.join(faf.SplitPath1(sys.argv[0]), "test_db3.sqlite")

    def setUp(self):
        self._init_order_id = "123456789"
        self._sell_order_id = "321654987"
        self._buy_order_id = "159732684"
        self._db = db.Simple()

    def test1_InitNewTrading(self):
        try:
            self._db.Init(self._db_filepath)
        except errors.NotAvailableTrading:
            self._db.InitNewTrading(self._init_order_id)
        self.assertEqual(self._db.GetInitialOrderId(), self._init_order_id)
        self.assertTrue(self._db.IsInit())

    def test2_SetSellOrderId(self):
        self._db.Init(self._db_filepath)
        self.assertEqual(self._db.GetInitialOrderId(), self._init_order_id)
        self.assertEqual(self._db.GetSellOrderId(), None)
        self.assertEqual(self._db.GetBuyOrderId(), None)
        self.assertTrue(self._db.IsInit())
        self._db.SetSellOrderId(self._sell_order_id)
        self.assertEqual(self._db.GetSellOrderId(), self._sell_order_id)
        self.assertEqual(self._db.GetBuyOrderId(), None)
        self.assertTrue(self._db.IsTrade())

    def test3_SetBuyOrderId(self):
        self._db.Init(self._db_filepath)
        self.assertEqual(self._db.GetInitialOrderId(), self._init_order_id)
        self.assertEqual(self._db.GetSellOrderId(), self._sell_order_id)
        self.assertEqual(self._db.GetBuyOrderId(), None)
        self.assertTrue(self._db.IsTrade())
        self._db.SetBuyOrderId(self._buy_order_id)
        self.assertEqual(self._db.GetSellOrderId(), self._sell_order_id)
        self.assertEqual(self._db.GetBuyOrderId(), self._buy_order_id)
        self.assertTrue(self._db.IsTrade())

    def test4_Complete(self):
        self._db.Init(self._db_filepath)
        self._db.SetAsComplete()
        self.assertTrue(self._db.IsComplete())
        self.assertFalse(self._db.IsTrade())
        self.assertFalse(self._db.IsInit())

    def test5_Complete(self):
        self.assertRaises(const.errors.NotAvailableTrading, self._db.Init, self._db_filepath)

    @classmethod
    def tearDownClass(cls):
        faf.DeleteFile1(cls._db_filepath)

class DB_Test4(unittest.TestCase):
    _db_filepath = os.path.join(faf.SplitPath1(sys.argv[0]), "test_db4.sqlite")

    def setUp(self):
        # db(s)
        self._init_order_id = "123456789"
        self._sell_order_id = "321654987"
        self._buy_order_id = "159732684"
        self._db = db.Simple()
        # strategy(s)
        self._strategy = ss.Simple()
        self._strategy.SetAvailableCurrency(1000000)
        self._strategy.SetCommissionBuy(0.998)
        self._strategy.SetCommissionSell(0.9994)
        self._strategy.SetCoefficient(2)
        self._strategy.SetPricePrecision1(3)
        self._strategy.SetQuantityPrecision1(8)
        self._strategy.SetProfit(1.01)
        self._strategy.Init(67.51, 500)
        self._strategy = self._strategy.ComputeToStep(3)

    def test1_SaveStrategy1(self):
        try:
            self._db.Init(self._db_filepath)
        except errors.NotAvailableTrading:
            self._db.InitNewTrading(self._init_order_id)
        self._db.SaveStrategy(self._strategy.CreateRecoveryString())
        self._db.SetSellOrderId(self._sell_order_id)
        self._db.SetBuyOrderId(self._buy_order_id)

    def test2_RestoreStrategy1(self):
        self._db.Init(self._db_filepath)
        recovery_strategy = type(self._strategy).RestoreFromRecoveryString(self._db.RestoreStrategy())
        self.assertTrue(self._strategy.GetStep(), recovery_strategy.GetStep())
        self.assertTrue(self._strategy.GetBuyRate(), recovery_strategy.GetBuyRate())
        self.assertTrue(self._strategy.GetSellRate(), recovery_strategy.GetSellRate())
        self.assertTrue(self._strategy.GetInfo(), recovery_strategy.GetInfo())
        self.assertEqual(self._db.GetSellOrderId(), self._sell_order_id)
        self.assertEqual(self._db.GetBuyOrderId(), self._buy_order_id)
        self.assertTrue(self._db.IsTrade())

    def test3_SaveStrategy2(self):
        self._db.Init(self._db_filepath)
        self._strategy = self._strategy.ComputeNextStep()
        self._db.SaveStrategy(self._strategy.CreateRecoveryString())

    def test4_RestoreStrategy2(self):
        self._db.Init(self._db_filepath)
        recovery_strategy = type(self._strategy).RestoreFromRecoveryString(self._db.RestoreStrategy())
        self._strategy = self._strategy.ComputeNextStep()
        self.assertTrue(self._strategy.GetStep(), recovery_strategy.GetStep())
        self.assertTrue(self._strategy.GetBuyRate(), recovery_strategy.GetBuyRate())
        self.assertTrue(self._strategy.GetSellRate(), recovery_strategy.GetSellRate())
        self.assertTrue(self._strategy.GetInfo(), recovery_strategy.GetInfo())
        self.assertEqual(self._db.GetSellOrderId(), self._sell_order_id)
        self.assertEqual(self._db.GetBuyOrderId(), self._buy_order_id)
        self.assertTrue(self._db.IsTrade())



    @classmethod
    def tearDownClass(cls):
        faf.DeleteFile1(cls._db_filepath)

if __name__ == "__main__":
    unittest.main()
