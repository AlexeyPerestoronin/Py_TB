import os
import re
import sys
import json
import decimal
import unittest

sys.path.insert(0, os.getcwd())

import common
import common.faf as faf
import connection.const.errors as c_errors
from connection import Exmo
class Test_Exmo(unittest.TestCase):
    def setUp(self):
        publick_key = faf.GetFileContent(faf.SearchAllFilesFromRoot2(os.getcwd(), re.compile(r"^.+?\.public\.key$"))[0])
        secret_key = bytes(faf.GetFileContent(faf.SearchAllFilesFromRoot2(os.getcwd(), re.compile(r"^.+?\.secret\.key$"))[0]), encoding="utf-8")
        self._exmo = Exmo()
        self._exmo.SetPublickKey(publick_key)
        self._exmo.SetSecretKey(secret_key)
        self._exmo.SetTakerCommissionPromotion(0.3)
        self._exmo.SetMakerCommissionPromotion(0.5)

    @staticmethod
    def GetTrades():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetTrades-BTC_USD.log", json.dumps(Exmo.GetTrades(pair="BTC_USD"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetTrades-USDT_RUB.log", json.dumps(Exmo.GetTrades(pair="USDT_RUB"), indent=4))

    @staticmethod
    def GetOrderBook():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetOrderBook-BTC_USD.log", json.dumps(Exmo.GetOrderBook(pair="BTC_USD"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetOrderBook-USDT_RUB.log", json.dumps(Exmo.GetOrderBook(pair="USDT_RUB"), indent=4))

    @staticmethod
    def GetTicker():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetTicker.log", json.dumps(Exmo.GetTicker(), indent=4))

    @staticmethod
    def GetPairSettings():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetPairSettings.log", json.dumps(Exmo.GetPairSettings(), indent=4))


    @staticmethod
    def GetCurrencyList():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetCurrencyList.log", json.dumps(Exmo.GetCurrencyList(), indent=4))

    def GetUserInfo(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserInfo.log", json.dumps(self._exmo.GetUserInfo(), indent=4))

    def GetCommissionForPair(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetTakerCommission-BTC_USD.log", json.dumps(self._exmo.GetTakerCommission("BTC_USD"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetMakerCommission-BTC_USD.log", json.dumps(self._exmo.GetMakerCommission("BTC_USD"), indent=4))

    def GetUserBalance(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserBalance-RUB.log", json.dumps(self._exmo.GetUserBalance("RUB"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserBalance-USDT.log", json.dumps(self._exmo.GetUserBalance("USDT"), indent=4))

    def GetUserOpenOrders(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserOpenOrders.log", json.dumps(self._exmo.GetUserOpenOrders(), indent=4))

    def GetUserCancelledOrders(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserCancelledOrders.log", json.dumps(self._exmo.GetUserCancelledOrders(), indent=4))

    def GetUserDeals(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserDeals-USDT_RUB.log", json.dumps(self._exmo.GetUserDeals("USDT_RUB"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserDeals-BTC_USDT.log", json.dumps(self._exmo.GetUserDeals("BTC_USDT"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserDeals-ETH_USDT.log", json.dumps(self._exmo.GetUserDeals("ETH_USDT"), indent=4))

    def GetOrderDeals(self):
        self.assertRaises(c_errors.OrderIsNotFoundByID, self._exmo.GetOrderDeals, "44333222111")
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetOrderDeals.log", json.dumps(self._exmo.GetOrderDeals("12591381569"), indent=4))

    def CreateOrder(self):
        pair = "ETH_USDT"
        current_buy_rate = self._exmo.GetCurrentBuyRate(pair)
        current_buy_rate /= 2
        current_buy_rate = float(decimal.Decimal(current_buy_rate).quantize(decimal.Decimal("1.00"), decimal.ROUND_CEILING))
        order_id = self._exmo.CreateOrder_BuyTotal(pair, 50, current_buy_rate)
        self.assertTrue(self._exmo.IsOrderOpen(order_id))
        self.assertRaises(c_errors.OrderIsNotFoundByID, self._exmo.GetOrderDeals, order_id)
        self._exmo.CancelOrder(order_id)
        self.assertRaises(c_errors.OrderIsNotFoundByID, self._exmo.GetOrderDeals, order_id)
        self.assertFalse(self._exmo.IsOrderOpen(order_id))

    def ComputeUserBalanceIn(self):
        print(self._exmo.ComputeUserBalanceIn("USDT"))
        print(self._exmo.ComputeUserBalanceIn("RUB"))

    def test_PerformTest(self):
        # self.GetTrades()
        # self.GetOrderBook()
        # self.GetTicker()
        # self.GetPairSettings()
        # self.GetCommissionForPair()
        # self.GetCurrencyList()
        # self.GetUserInfo()
        # self.GetUserBalance()
        # self.GetUserOpenOrders()
        # self.GetUserCancelledOrders()
        # self.GetUserDeals()
        # self.GetOrderDeals()
        # self.CreateOrder()
        # self.ComputeUserBalanceIn()
        pass

if __name__ == "__main__":
    unittest.main()
