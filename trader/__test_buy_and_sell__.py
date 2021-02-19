import os
import sys
import unittest

sys.path.insert(0, os.getcwd())

import trader
import connection as con
import common.faf as faf
import strategy.stairs as ss

PARAMS_1 = \
{
    "ID" : "1-SoftCostIncreaseDS",
    "PAIR" : "ETH_USD",
    "INIT_COST" : "10",
    "DB_FILENAME" : "st.sqlite",
    "SAVE_CATALOG" : ".trading",
    "COMPLETED_POLICY" : {
        "ID" : "InfinityCP",
        "PARAMS" : {
            "STOP_TRIGGER" : 100
        }
    },
    "STRATEGY" : {
        "ID" : "BsRcSoftCostIncreaseS",
        "PARAMS" : {
            "GLOBAL_COST_PRECISION": "4",
            "GLOBAL_COEFFICIENT_1": "2",
            "GLOBAL_PROFIT": "1.003",
            "GLOBAL_AVAILABLE_CURRENCY": "200",
            "GLOBAL_SELL_COMMISSION_CONCESSION": "0.78",
            "GLOBAL_BUY_COMMISSION_CONCESSION": "0.78",
        }
    }
}

connection = con.Exmo()
# connection.SetPublickKey("")
# connection.SetSecretKey("")
connection.SetTakerCommissionPromotion(1)
connection.SetMakerCommissionPromotion(1)

class TestTrader(unittest.TestCase, trader.BuyAndSell):
    def setUp(self):
        trader.BuyAndSell.__init__(self)
        self.SetParameters(PARAMS_1)
        self.SetConnection(connection)
        self.Init()

    @classmethod
    def tearDownClass(cls):
        faf.DeleteFile1(os.path.join(PARAMS_1["SAVE_CATALOG"], PARAMS_1["DB_FILENAME"]))

class Test1(TestTrader):
    def test1(self):
        self._db.SetInitOrder(self._db.CreateId())
        self._strategy.SetInitRate("1400")
        self._strategy.SetInitCost("10")
        self._strategy.Init()
        self._db.SetSellOrder(self._db.CreateId())
        self._db.SetBuyOrder(self._db.CreateId())

    def test2(self):
        self._strategy = type(self._strategy).RestoreFromRecoveryString(self._db.GetStrategyRecovery())
        
        self.assertEqual(self._strategy.GetStep(), 1)
        self._strategy = self._strategy.ComputeNextStep()
        self._db.SetSellOrder(self._db.CreateId())
        self._db.SetBuyOrder(self._db.CreateId())

    def test3(self):
        self._strategy = type(self._strategy).RestoreFromRecoveryString(self._db.GetStrategyRecovery())
        self.assertEqual(self._strategy.GetStep(), 2)
        self._strategy = self._strategy.ComputeNextStep()
        self._db.SetSellOrder(self._db.CreateId())
        self._db.SetBuyOrder(self._db.CreateId())

    def test4(self):
        self._strategy = type(self._strategy).RestoreFromRecoveryString(self._db.GetStrategyRecovery())
        self.assertEqual(self._strategy.GetStep(), 3)
        self._strategy = self._strategy.ComputeNextStep()
        self._db.SetSellOrder(self._db.CreateId())
        self._db.SetBuyOrder(self._db.CreateId())

if __name__ == "__main__":
    unittest.main()
