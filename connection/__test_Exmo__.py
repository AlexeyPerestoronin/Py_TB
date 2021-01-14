import os
import re
import sys
import json
import unittest

sys.path.insert(0, os.getcwd())

import common
import common.faf as faf
from connection import Exmo

class Test_Exmo(unittest.TestCase):
    def setUp(self):
        publick_key = faf.GetFileContent(faf.SearchAllFilesFromRoot2(os.getcwd(), re.compile(r"^.+?\.public\.key$"))[0])
        secret_key = bytes(faf.GetFileContent(faf.SearchAllFilesFromRoot2(os.getcwd(), re.compile(r"^.+?\.secret\.key$"))[0]), encoding="utf-8")
        self.__exmo = Exmo()
        self.__exmo.SetPublickKey(publick_key)
        self.__exmo.SetSecretKey(secret_key)

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
    def GetCommissionForPair():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetCommissionForPair-BTC_USD.log", json.dumps(Exmo.GetCommissionForPair("BTC_USD"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetCommissionForPair-BTC_USDT.log", json.dumps(Exmo.GetCommissionForPair("BTC_USDT"), indent=4))

    @staticmethod
    def GetCurrencyList():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetCurrencyList.log", json.dumps(Exmo.GetCurrencyList(), indent=4))

    def GetUserInfo(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserInfo.log", json.dumps(self.__exmo.GetUserInfo(), indent=4))

    def GetUserBalance(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserBalance-RUB.log", json.dumps(self.__exmo.GetUserBalance("RUB"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserBalance-USDT.log", json.dumps(self.__exmo.GetUserBalance("USDT"), indent=4))

    def GetUserOpenOrders(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserOpenOrders.log", json.dumps(self.__exmo.GetUserOpenOrders(), indent=4))

    def GetUserCancelledOrders(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserCancelledOrders.log", json.dumps(self.__exmo.GetUserCancelledOrders(), indent=4))

    def GetUserDeals(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserDeals-USDT_RUB.log", json.dumps(self.__exmo.GetUserDeals("USDT_RUB"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserDeals-BTC_USDT.log", json.dumps(self.__exmo.GetUserDeals("BTC_USDT"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetUserDeals-ETH_USDT.log", json.dumps(self.__exmo.GetUserDeals("ETH_USDT"), indent=4))

    def GetOrderDeals(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetOrderDeals-sell-order.log", json.dumps(self.__exmo.GetOrderDeals("11589112646"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetOrderDeals-buy-order.log", json.dumps(self.__exmo.GetOrderDeals("11606216514"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetOrderDeals-buy-match.log", json.dumps(self.__exmo.GetOrderDeals("11654835769"), indent=4))

    def CreateOrder_Buy_Check_Cancel(self):
        order_id = self.__exmo.CreateOrder_Buy("USDT_RUB", 1, 50)
        self.assertTrue(self.__exmo.IsOrderOpen(order_id))
        self.__exmo.CancelOrder(order_id)
        self.assertFalse(self.__exmo.IsOrderOpen(order_id))

    def CreateOrder_BuyTotal_Check_Cancel(self):
        order_id = self.__exmo.CreateOrder_BuyTotal("USDT_RUB", 100, 50)
        self.assertTrue(self.__exmo.IsOrderOpen(order_id))
        self.__exmo.CancelOrder(order_id)
        self.assertFalse(self.__exmo.IsOrderOpen(order_id))

    def ComputeUserBalanceIn(self):
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "ComputeUserBalanceIn-USDT.log", json.dumps(self.__exmo.ComputeUserBalanceIn("USDT"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "ComputeUserBalanceIn-RUB.log", json.dumps(self.__exmo.ComputeUserBalanceIn("RUB"), indent=4))

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
        # self.CreateOrder_Buy_Check_Cancel()
        # self.CreateOrder_BuyTotal_Check_Cancel()
        self.ComputeUserBalanceIn()
        pass

if __name__ == "__main__":
    unittest.main()
