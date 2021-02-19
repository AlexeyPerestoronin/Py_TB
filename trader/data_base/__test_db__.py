import os
import re
import sys
import time
import json
import shutil
import unittest

sys.path.insert(0, os.getcwd())

import common.faf as faf

import strategy
import strategy.stairs.buy_and_sell.rate_computed as ss_bs_rc

import trader
import trader.data_base.tables.consts as table_const
import trader.data_base.tables.errors as table_error

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
            "ID" : "DEPENDENT",
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
        return self._strategy.GetStepProfitLeft()


    def setUp(self):
        # strategy
        self._strategy = ss_bs_rc.BsRcSimple()
        self._strategy.SetAvailableCurrency("1400")
        self._strategy.SetCommissionBuy("1")
        self._strategy.SetCommissionSell("1")
        self._strategy.SetCoefficient1("1.5")
        self._strategy.SetRatePrecision("4")
        self._strategy.SetCostPrecision("4")
        self._strategy.SetQuantityPrecision("8")
        self._strategy.SetProfit("1.002")
        self._strategy.SetInitRate("1300")
        self._strategy.SetInitCost("10")
        self._strategy.Init()
        # db
        self._db = trader.data_base.DbSimple()
        self._db.SetCallbackGetStrategyRecoverystring(self._GetStrategyRecoverystring)
        self._db.SetCallbackGetStrategyPreview(self._GetStrategyPreview)
        self._db.SetCallbackGetStrategyProfit(self._GetStrategyProfit)
        self._db.SetCallbackGetOrderTrueview(GetOrderTrueview)
        self._db.SetFilePath(self._db_filepath)
        self._db.SetParams(self._params)

    @classmethod
    def tearDownClass(cls):
        faf.DeleteFile1(cls._db_filepath)

class Test1_DB(CommonParams, unittest.TestCase):
    def test1(self):
        self.assertRaises(table_error.TraderIsNotCreate, self._db.GetTraderId)
        self.assertRaises(table_error.TraderIsNotCreate, self._db.GetTraderPtofit)
        self.assertRaises(table_error.TraderIsNotCreate, self._db.GetTraderStatus)
        self.assertRaises(table_error.StrategyIsNotCreate, self._db.GetStrategyId)
        self.assertRaises(table_error.StrategyIsNotCreate, self._db.SetStrategyAsWait)
        self.assertRaises(table_error.StrategyIsNotCreate, self._db.GetStrategyRecovery)
        self.assertRaises(table_error.StrategyIsNotCreate, self._db.GetStrategyPreview)
        self.assertRaises(table_error.StrategyIsNotCreate, self._db.GetStrategyProfit)
        self.assertRaises(table_error.StrategyIsNotCreate, self._db.GetStrategyStatus)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)

    def test2(self):
        self._db.Init()
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.VOID)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.VOID)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)

    def test3(self):
        self._db.Init()
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.VOID)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.VOID)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)

    def test4(self):
        self._db.Init()
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.VOID)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.VOID)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)
        self._db.SetInitOrder(self._o_i_id)
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.INIT)
        self.assertEqual(self._db.GetInitOrder(), self._o_i_id)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)

    def test5(self):
        self._db.Init()
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.INIT)
        self.assertEqual(self._db.GetInitOrder(), self._o_i_id)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)
        self._db.SetSellOrder(self._o_s_id)
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.TRADE)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)

    def test6(self):
        self._db.Init()
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.TRADE)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)
        self._db.SetBuyOrder(self._o_b_id)
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.TRADE)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id)

    def test7(self):
        self._db.Init()
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.TRADE)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id)
        self._db.SetBuyOrder(self._o_b_id + self._o_b_id)
        self._db.SetSellOrder(self._o_s_id + self._o_s_id)
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.TRADE)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id + self._o_s_id)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id + self._o_b_id)

    def test8(self):
        self._db.Init()
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.TRADE)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id + self._o_s_id)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id + self._o_b_id)
        self._db.FinishTrader()
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)
        self.assertRaises(table_error.StrategyIsNotCreate, self._db.GetStrategyStatus)
        self.assertRaises(table_error.TraderIsNotCreate, self._db.GetTraderStatus)

    def test9(self):
        self._db.Init()
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.VOID)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.VOID)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)
        self._o_i_id = self._db.CreateId()
        self._db.InitNewTrading(self._o_i_id)
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.INIT)
        self.assertEqual(self._db.GetInitOrder(), self._o_i_id)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)
        self._o_i_id = self._db.CreateId()
        self._db.InitNewTrading(self._o_i_id)
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.INIT)
        self.assertEqual(self._db.GetInitOrder(), self._o_i_id)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)
        self._o_i_id = self._db.CreateId()
        self._db.InitNewTrading(self._o_i_id)
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.INIT)
        self.assertEqual(self._db.GetInitOrder(), self._o_i_id)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetBuyOrder)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.TRADE)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetSellOrder)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self.assertEqual(self._db.GetTraderStatus(), table_const.Status.Trader.DURING)
        self.assertEqual(self._db.GetStrategyStatus(), table_const.Status.Strategy.TRADE)
        self.assertRaises(table_error.OrderIsNotCreate, self._db.GetInitOrder)
        self.assertEqual(self._db.GetSellOrder(), self._o_s_id)
        self.assertEqual(self._db.GetBuyOrder(), self._o_b_id)
        self._db.FinishTrader()

class Test2_DB(CommonParams, unittest.TestCase):
    def test1(self):
        self._db.Init()
        self._o_i_id = self._db.CreateId()
        self._db.SetInitOrder(self._o_i_id)

    def test2(self):
        self._db.Init()
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)

    def test3(self):
        self._db.Init()
        self._strategy = self._strategy.ComputeToStep(1)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)

    def test4(self):
        self._db.Init()
        self._strategy = self._strategy.ComputeToStep(2)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)

    def test5(self):
        self._strategy = self._strategy.ComputeToStep(2)
        self._db.Init()
        self._db.InitNewTrading(self._db.CreateId())
        self._strategy = self._strategy.ComputeToStep(1)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)

    def test6(self):
        self._db.Init()
        self._strategy = self._strategy.ComputeToStep(2)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)

    def test7(self):
        self._strategy = self._strategy.ComputeToStep(2)
        self._db.Init()
        self._strategy = self._strategy.ComputeToStep(3)
        self._o_s_id = self._db.CreateId()
        self._db.SetSellOrder(self._o_s_id)
        self._o_b_id = self._db.CreateId()
        self._db.SetBuyOrder(self._o_b_id)

    def test8(self):
        self._strategy = self._strategy.ComputeToStep(3)
        self._db.Init()
        self._db.FinishTrader()

class Test3_DB(CommonParams, unittest.TestCase):
    def test1(self):
        self._db.Init()
        self._db.SetInitOrder(self._db.CreateId())
        self._db.SetSellOrder(self._db.CreateId())
        self._db.SetBuyOrder(self._db.CreateId())
        self.assertEqual(self._db.GetTraderCompletedStrategy(), 0)

    def test2(self):
        self._db.Init()
        self.assertEqual(self._db.GetTraderCompletedStrategy(), 0)
        self._db.InitNewTrading(self._db.CreateId())
        self._db.SetInitOrder(self._db.CreateId())
        self._db.SetSellOrder(self._db.CreateId())
        self._db.SetBuyOrder(self._db.CreateId())
        self.assertEqual(self._db.GetTraderCompletedStrategy(), 1)

    def test3(self):
        self._db.Init()
        self.assertEqual(self._db.GetTraderCompletedStrategy(), 1)
        self._db.InitNewTrading(self._db.CreateId())
        self._db.SetInitOrder(self._db.CreateId())
        self._db.SetSellOrder(self._db.CreateId())
        self._db.SetBuyOrder(self._db.CreateId())
        self.assertEqual(self._db.GetTraderCompletedStrategy(), 2)

    def test4(self):
        self._db.Init()
        self.assertEqual(self._db.GetTraderCompletedStrategy(), 2)
        self._db.FinishCurrentStrategy()
        self.assertEqual(self._db.GetTraderCompletedStrategy(), 3)
        self._db.FinishTrader()

if __name__ == "__main__":
    unittest.main()
