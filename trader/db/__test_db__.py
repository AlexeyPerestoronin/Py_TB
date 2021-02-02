import os
import re
import sys
import time
import json
import shutil
import unittest

sys.path.insert(0, os.getcwd())

import common.faf as faf
import trader.db as db
import trader.const as const
import trader.const.errors as errors

import strategy
import strategy.stairs as ss

def GetOrderTrueview(order_id):
    return json.dumps({
        "type": "sell",
        "in_currency": "RUB",
        "in_amount": "101.40551849",
        "out_currency": "USDT",
        "out_amount": "1.41716887",
        "trades": [
            {
                "trade_id": 226105506,
                "client_id": 0,
                "date": 1609732880,
                "type": "sell",
                "pair": "USDT_RUB",
                "order_id": 11589112646,
                "quantity": "1.41716887",
                "price": "71.555",
                "amount": "101.40551849",
                "exec_type": "maker",
                "commission_amount": "0.40562207",
                "commission_currency": "RUB",
                "commission_percent": "0.4"
            }
        ]})

class CommonParams:
    _o_i_id = "111"
    _o_s_id = "222"
    _o_b_id = "333"
    _params = json.dumps({
        "pair" : "ETH_RUB",
        "init_cost" : 500,
        "save_catalog" : "SC-ETH_RUB",
        "strategy" : {
            "ID" : "STAIRS_DEPENDENT",
            "profit" : 1.001,
            "coefficient" : 1.5,
            "volume_precision" : 8
        }
    })
    _db_filepath = os.path.join(faf.SplitPath1(sys.argv[0]), "test_db.sqlite")

    def _GetStrategyRecoverystring(self):
        return self._strategy.CreateRecoveryString()

    def _GetStrategyPreview(self):
        return strategy.StrategyPreview(self._strategy).GetPreview()

    def _GetStrategyProfit(self):
        return self._strategy.GetStepProfit()

    def setUp(self):
        # strategy
        self._strategy = ss.Simple()
        self._strategy.SetAvailableCurrency(1400)
        self._strategy.SetCommissionBuy(1)
        self._strategy.SetCommissionSell(1)
        self._strategy.SetCoefficient(1.5)
        self._strategy.SetPricePrecision1(4)
        self._strategy.SetQuantityPrecision1(8)
        self._strategy.SetProfit(1.002)
        self._strategy.Init(1300, 10)
        # db
        self._db = db.Simple()
        self._db.RegGetStrategyRecoverystring(self._GetStrategyRecoverystring)
        self._db.RegGetStrategyPreview(self._GetStrategyPreview)
        self._db.RegGetStrategyProfit(self._GetStrategyProfit)
        self._db.RegGetOrderTrueview(GetOrderTrueview)

    @classmethod
    def tearDownClass(cls):
        faf.DeleteFile1(cls._db_filepath)

class Test1_DB(CommonParams, unittest.TestCase):
    def test1(self):
        self.assertRaises(const.errors.TraderIsNotCreate, self._db.GetId)
        self.assertRaises(const.errors.TraderIsNotCreate, self._db.GetPtofit)
        self.assertRaises(const.errors.TraderIsNotCreate, self._db.GetStatus)
        self.assertRaises(const.errors.StrategyIsNotCreate, self._db.GetStrategyId)
        self.assertRaises(const.errors.StrategyIsNotCreate, self._db.SetStrategyAsWait)
        self.assertRaises(const.errors.StrategyIsNotCreate, self._db.GetStrategyRecovery)
        self.assertRaises(const.errors.StrategyIsNotCreate, self._db.GetStrategyPreview)
        self.assertRaises(const.errors.StrategyIsNotCreate, self._db.GetStrategyProfit)
        self.assertRaises(const.errors.StrategyIsNotCreate, self._db.GetStrategyStatus)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)

    def test2(self):
        self._db.Init(self._db_filepath, self._params)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.VOID)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.VOID)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)

    def test3(self):
        self._db.Init(self._db_filepath, self._params)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.VOID)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.VOID)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)

    def test4(self):
        self._db.Init(self._db_filepath, self._params)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.VOID)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.VOID)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)
        self._db.SetInitOrder(self._o_i_id)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.INIT)
        self.assertEqual(self._db.GetInitOrder(), self._o_i_id)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)

    def test5(self):
        self._db.Init(self._db_filepath, self._params)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.INIT)
        self.assertEqual(self._db.GetInitOrder(), self._o_i_id)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)
        self._db.SetSellOrder(self._o_s_id)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.TRADE)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)

    def test6(self):
        self._db.Init(self._db_filepath, self._params)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.TRADE)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)
        self._db.SetBuyOrder(self._o_b_id)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.TRADE)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id)

    def test7(self):
        self._db.Init(self._db_filepath, self._params)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.TRADE)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id)
        self._db.SetBuyOrder(self._o_b_id + self._o_b_id)
        self._db.SetSellOrder(self._o_s_id + self._o_s_id)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.TRADE)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id + self._o_s_id)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id + self._o_b_id)

    def test8(self):
        self._db.Init(self._db_filepath, self._params)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.TRADE)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id + self._o_s_id)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id + self._o_b_id)
        self._db.Finish()
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)
        self.assertRaises(const.errors.StrategyIsNotCreate, self._db.GetStrategyStatus)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.FINISHED)

    def test9(self):
        self._db.Init(self._db_filepath, self._params)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.VOID)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.VOID)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)
        self._o_i_id = self._db.CreateId()
        self._db.InitNewTrading(self._o_i_id)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.INIT)
        self.assertEqual(self._db.GetInitOrder(), self._o_i_id)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)
        self._o_i_id = self._db.CreateId()
        self._db.InitNewTrading(self._o_i_id)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.INIT)
        self.assertEqual(self._db.GetInitOrder(), self._o_i_id)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)
        self._o_i_id = self._db.CreateId()
        self._db.InitNewTrading(self._o_i_id)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.INIT)
        self.assertEqual(self._db.GetInitOrder(), self._o_i_id)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetBuyOrder)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.TRADE)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self.assertEqual(self._db.GetStatus(), const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), const.Status.Strategy.TRADE)
        self.assertRaises(const.errors.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id)
        self._db.Finish()

class Test2_DB(CommonParams, unittest.TestCase):
    def test1(self):
        self._db.Init(self._db_filepath, self._params)
        self._o_i_id = self._db.CreateId()
        self._db.SetInitOrder(self._o_i_id)
    
    def test2(self):
        self._db.Init(self._db_filepath, self._params)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)

    def test3(self):
        self._db.Init(self._db_filepath, self._params)
        self._strategy = self._strategy.ComputeToStep(1)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)
    
    def test4(self):
        self._db.Init(self._db_filepath, self._params)
        self._strategy = self._strategy.ComputeToStep(2)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)

    def test5(self):
        self._strategy = self._strategy.ComputeToStep(2)
        self._db.Init(self._db_filepath, self._params)
        self._db.InitNewTrading(self._db.CreateId())
        self._strategy = self._strategy.ComputeToStep(1)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)

    def test6(self):
        self._db.Init(self._db_filepath, self._params)
        self._strategy = self._strategy.ComputeToStep(2)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)

    def test7(self):
        self._strategy = self._strategy.ComputeToStep(2)
        self._db.Init(self._db_filepath, self._params)
        self._strategy = self._strategy.ComputeToStep(3)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)

    def test8(self):
        self._strategy = self._strategy.ComputeToStep(3)
        self._db.Init(self._db_filepath, self._params)
        self._db.Finish()

class Test3_DB(CommonParams, unittest.TestCase):
    def test1(self):
        self._db.Init(self._db_filepath, self._params)
        self._db.SetInitOrder(self._db.CreateId())
        self._db.SetSellOrder(self._db.CreateId())
        self._db.SetBuyOrder(self._db.CreateId())
        self.assertEqual(self._db.GetCompletedStrategy(), 0)

    def test2(self):
        self._db.Init(self._db_filepath, self._params)
        self.assertEqual(self._db.GetCompletedStrategy(), 0)
        self._db.InitNewTrading(self._db.CreateId())
        self._db.SetInitOrder(self._db.CreateId())
        self._db.SetSellOrder(self._db.CreateId())
        self._db.SetBuyOrder(self._db.CreateId())
        self.assertEqual(self._db.GetCompletedStrategy(), 1)

    def test3(self):
        self._db.Init(self._db_filepath, self._params)
        self.assertEqual(self._db.GetCompletedStrategy(), 1)
        self._db.InitNewTrading(self._db.CreateId())
        self._db.SetInitOrder(self._db.CreateId())
        self._db.SetSellOrder(self._db.CreateId())
        self._db.SetBuyOrder(self._db.CreateId())
        self.assertEqual(self._db.GetCompletedStrategy(), 2)

    def test4(self):
        self._db.Init(self._db_filepath, self._params)
        self.assertEqual(self._db.GetCompletedStrategy(), 2)
        self._db.FinishStrategy()
        self.assertEqual(self._db.GetCompletedStrategy(), 3)
        self._db.Finish()

if __name__ == "__main__":
    unittest.main()
