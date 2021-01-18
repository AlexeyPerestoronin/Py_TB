import os
import re
import sys
import time
import shutil
import unittest

sys.path.insert(0, os.getcwd())

from trader import Simple

import connection as con
import common.faf as faf
import strategy.stairs as ss

class Keys:
    def __init__(self):
        self._publick_key = faf.GetFileContent(faf.SearchAllFilesFromRoot2(os.getcwd(), re.compile(r"^.+?\.public\.key$"))[0])
        self._secret_key = bytes(faf.GetFileContent(faf.SearchAllFilesFromRoot2(os.getcwd(), re.compile(r"^.+?\.secret\.key$"))[0]), encoding="utf-8")

class SimpleStump(unittest.TestCase, Simple):
    save_catalog_test = os.path.join(faf.SplitPath1(sys.argv[0]), "test")

    def setUp(self):
        self._strategy = ss.Simple()
        self._strategy.SetCommissionBuy(1.0)
        self._strategy.SetCommissionSell(1.0)
        self._strategy.SetCoefficient(2)
        self._strategy.SetPricePrecision1(6)
        self._strategy.SetQuantityPrecision1(8)
        self._strategy.SetProfit(1.1)
        self._strategy.Init(1000, 100)
        self._strategy = self._strategy.ComputeToStep(3)
        self._sell_order_id = 101
        self._buy_order_id = 202

    def test_Save_Restore(self):
        strategy_before = self._strategy
        sell_order_id_before = self._sell_order_id
        buy_order_id_before = self._buy_order_id
        self.SetSaveCatalog(self.save_catalog_test)
        self._Save()
        self._Restore()
        self.assertTrue(sell_order_id_before, self._sell_order_id)
        self.assertTrue(buy_order_id_before, self._buy_order_id)
        self.assertTrue(strategy_before.GetID(), self._strategy.GetID())
        self.assertTrue(strategy_before.GetStep(), self._strategy.GetStep())
        self.assertTrue(strategy_before.GetSellRate(), self._strategy.GetSellRate())
        self.assertTrue(strategy_before.GetBuyRate(), self._strategy.GetBuyRate())
        self.assertTrue(strategy_before.GetInfo(), self._strategy.GetInfo())

    def tearDown(self):
        shutil.rmtree(self.Finish())

class Test_Simple1(unittest.TestCase, Keys):
    def setUp(self):
        Keys.__init__(self)
        connection = con.Exmo()
        connection.SetPublickKey(self._publick_key)
        connection.SetSecretKey(self._secret_key)
        strategy = ss.Simple()
        strategy.SetProfit(1.01)
        strategy.SetCoefficient(2)
        strategy.SetQuantityPrecision1(8)
        self._trader = Simple(connection, strategy)

    def test_Trading1(self):
        save_catalog = os.path.join(faf.SplitPath1(sys.argv[0]), "SC-USDT_RUB")
        self._trader.SetInitCost(500)
        self._trader.SetPair("USDT_RUB")
        self._trader.SetSaveCatalog(save_catalog)
        # self._trader.Start()
        # self._trader.Iterate()

class Test_Simple2(unittest.TestCase, Keys):
    def setUp(self):
        Keys.__init__(self)
        connection = con.Exmo()
        connection.SetPublickKey(self._publick_key)
        connection.SetSecretKey(self._secret_key)
        strategy = ss.Dependency()
        strategy.SetProfit(1.01)
        strategy.SetCoefficient(2)
        strategy.SetQuantityPrecision1(8)
        self._trader = Simple(connection, strategy)

    def test_Trading1(self):
        save_catalog = os.path.join(faf.SplitPath1(sys.argv[0]), "SC-BTC_USDT")
        self._trader.SetInitCost(10)
        self._trader.SetPair("BTC_USDT")
        self._trader.SetSaveCatalog(save_catalog)
        # self._trader.Start()
        # self._trader.Iterate()

if __name__ == "__main__":
    unittest.main()
