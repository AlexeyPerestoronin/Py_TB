import os
import sys
import json
import unittest

sys.path.insert(0, os.getcwd())

import common
import common.faf as faf
from connection import Exmo

class Test_Exmo(unittest.TestCase):
    def setUp(self):
        pass

    @staticmethod
    def test_GetTrades():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetTrades-BTC_USD.log", json.dumps(Exmo.GetTrades(pair="BTC_USD"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetTrades-USDT_RUB.log", json.dumps(Exmo.GetTrades(pair="USDT_RUB"), indent=4))

    @staticmethod
    def test_GetOrderBook():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetOrderBook-BTC_USD.log", json.dumps(Exmo.GetOrderBook(pair="BTC_USD"), indent=4))
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetOrderBook-USDT_RUB.log", json.dumps(Exmo.GetOrderBook(pair="USDT_RUB"), indent=4))

    @staticmethod
    def test_GetTicker():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetTicker.log", json.dumps(Exmo.GetTicker(), indent=4))

    @staticmethod
    def test_GetPairSettings():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetPairSettings.log", json.dumps(Exmo.GetPairSettings(), indent=4))

    @staticmethod
    def test_GetCurrencyList():
        faf.SaveContentToFile2(faf.SplitPath1(sys.argv[0]), "GetCurrencyList.log", json.dumps(Exmo.GetCurrencyList(), indent=4))

if __name__ == "__main__":
    unittest.main()
