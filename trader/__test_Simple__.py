import os
import re
import sys
import time
import shutil
import unittest

sys.path.insert(0, os.getcwd())

import trader
import connection as con
import common.faf as faf
import strategy.stairs as ss

PARAMS_1 = {
    "id" : "test trading",
    "pair" : "ETH_RUB",
    "init_cost" : 100,
    "db_filename" : "test.sqlite",
    "save_catalog" : ".trading",
    "completed_policy" : {
        "id" : "FIXED_COMPLETED_STRATEGY",
        "params" : 1
    },
    "strategy" : {
        "id" : "FIXED_BUY_COST_S",
        "profit" : 1.01,
        "coefficient" : 1.5,
        "quantity_precision" : 8,
        "available_currency" : 1300
    }
}

class TestTrader(unittest.TestCase, trader.Simple):
    def setUp(self):
        trader.Simple.__init__(self)
        self.SetParameters(PARAMS_1)
        self.Init()

    @classmethod
    def tearDownClass(cls):
        faf.DeleteFile1(os.path.join(PARAMS_1["save_catalog"], PARAMS_1["db_filename"]))

class Test1(TestTrader):
    def test1(self):
        self._db.SetInitOrder(self._db.CreateId())
        self._strategy.SetQuantityPrecision1(8)
        self._strategy.SetPricePrecision1(4)
        self._strategy.SetCommissionSell(1.0)
        self._strategy.SetCommissionBuy(1.0)
        self._strategy.Init(1400, 100)
        self._db.SetSellOrder(self._db.CreateId())
        self._db.SetBuyOrder(self._db.CreateId())

    def test2(self):
        self._strategy = type(self._strategy).RestoreFromRecoveryString(self._db.GetStrategyRecovery())

if __name__ == "__main__":
    unittest.main()
