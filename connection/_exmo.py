import copy
import time
import json
import hmac
import urllib
import hashlib
import http.client

# brief: implements logic for interaction with Exmo-exchange
class Exmo:
    url = "api.exmo.com"
    api_version = "v1.1"

    def __init__(self, publick_key, secret_key):
        self.__publick_key = publick_key
        self.__secret_key = secret_key

    # NOTE: for detail information about all below class-methods see https://documenter.getpostman.com/view/10287440/SzYXWKPi#public_api?utm_source=site&utm_medium=articles%22

    # brief: gets list of the deals in currency pair
    @staticmethod
    def GetTrades(pair):
        return Exmo.Query("trades", pair=pair)

    # brief: gets the book of current orders on the currency pair
    @staticmethod
    def GetOrderBook(pair, limit=100):
        return Exmo.Query("order_book", pair=pair, limit=limit)

    # brief: gets statistics on prices and volume of trades by currency pairs
    @staticmethod
    def GetTicker():
        return Exmo.Query("ticker")

    # brief: gets currency pair setting
    @staticmethod
    def GetPairSettings():
        return Exmo.Query("pair_settings")

    # brief: gets avaliable list of currency
    @staticmethod
    def GetCurrencyList():
        return Exmo.Query("currency")

    # brief: gets information about user's account
    def GetUserInfo(self):
        return self.QueryPrivate("user_info")

    # brief: gets the list of user's open (active) orders
    def GetUserOpenOrders(self):
        return self.QueryPrivate("user_open_orders")

    # brief: gets the list of user's candelled orders
    def GetUserCancelledOrders(self, limit=100, offset=0):
        return self.QueryPrivate("user_cancelled_orders", limit=limit, offset=offset)

    # brief: gets the list of user's deals
    def GetUserDeals(self, pair, limit=100, offset=0):
        return self.QueryPrivate("user_trades", pair=pair, limit=limit, offset=offset)

    # brief: gets the list of trade's deals
    def GetOrderDeals(self, order_id):
        return self.QueryPrivate("order_trades", order_id=order_id)

    # brief: creates an buy-order
    def CreateOrder_Buy(self, pair, buy_quantity, buy_rate):
        return self.QueryPrivate("order_create", type="buy", pair=pair, quantity=buy_quantity, price=buy_rate)

    # brief: creates an buy-order at current market buy-rate
    def CreateOrder_BuyMarket(self, pair, buy_quantity):
        return self.QueryPrivate("order_create", type="market_buy", pair=pair, quantity=buy_quantity, price=0)

    # brief: creates an buy-order at current market buy-rate and predefined total-cost
    def CreateOrder_BuyMarketTotal(self, pair, total_cost):
        return self.QueryPrivate("order_create", type="market_buy_total", pair=pair, quantity=total_cost, price=0)

    # brief: creates an sell-order
    def CreateOrder_Sell(self, pair, sell_quantity, sell_rate):
        return self.QueryPrivate("order_create", type="sell", pair=pair, quantity=sell_quantity, price=sell_rate)

    # brief: creates an sell-order at current market sell-rate
    def CreateOrder_SellMarket(self, pair, quantity):
        return self.QueryPrivate("order_create", type="market_sell", pair=pair, quantity=quantity, price=0)

    # brief: creates an sell-order at current market sell-rate and predefined total-cost
    def CreateOrder_SellMarketTotal(self, pair, total_cost):
        return self.QueryPrivate("order_create", type="market_sell_total", pair=pair, quantity=total_cost, price=0)

    # brief: cancels the trade-order by its id
    def CancelOrder(self, order_id):
        return self.QueryPrivate("order_cancel", order_id=order_id)

    # brief: creates stop-buy-order for predefined buy-rate
    def CreateStopOrder_Buy(self, pair, buy_quantity, trigger_buy_rate):
        return self.QueryPrivate("stop_market_order_create", type="buy", pair=pair, quantity=buy_quantity, trigger_price=trigger_buy_rate)

    # brief: creates stop-sell-order for predefined sell-rate
    def CreateStopOrder_Sell(self, pair, sell_quantity, trigger_sell_rate):
        return self.QueryPrivate("stop_market_order_create", type="buy", pair=pair, quantity=sell_quantity, trigger_price=trigger_sell_rate)

    # brief: cancels the stop-trade-order by its id
    def CancelStopOrder(self, stop_order_id):
        return self.QueryPrivate("stop_market_order_cancel", parent_order_id=stop_order_id)

    # brief: performs https-get/post requests to private-API of Exmo-exchange
    # param: api_method - the requested method
    # param: params - params for the specifing of the method
    # return: json-string with response on the requested method
    def QueryPrivate(self, api_method, **params):
        return Exmo.Query(api_method, self.__publick_key, self.__secret_key, **params)

    # NOTE: for detailed information about structure of code in below see https://github.com/exmo-dev/exmo_api_lib/blob/master/rest/python/exmo3.py

    # brief: performs https-get/post requests to Exmo-exchange
    # param: api_method - the requested method
    # param: publick_key - the publick-key of the target user
    # param: secret_key - the private-key of the target user
    # param: params - params for the specifing of the method
    # return: json-string with response on the requested method
    @staticmethod
    def Query(api_method, publick_key="STUMP", secret_key=bytes("STUMP", encoding="utf-8"), **params):
        def ComputeHash(data):
            """ computes hash-value from target https-request """
            hash = hmac.new(key=secret_key, digestmod=hashlib.sha512)
            hash.update(data.encode('utf-8'))
            return hash.hexdigest()

        params["nonce"] = int(round(time.time() * 1000))
        params = urllib.parse.urlencode(params)
        headers = {
            # type of data for sign
            "Content-type": "application/x-www-form-urlencoded",
            # publick-key for check data sign
            "Key": publick_key,
            # signed data for request
            "Sign": ComputeHash(params) # подписанные данные
        }
        conn = http.client.HTTPSConnection(Exmo.url)
        conn.request("POST", "/" + Exmo.api_version + "/" + api_method, params, headers)
        response = conn.getresponse().read()
        conn.close()
        result = json.loads(response.decode('utf-8'))
        if "error" in result and result["error"]:
            raise result["error"]
        return result
