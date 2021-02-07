import copy
import time
import json
import hmac
import urllib
import hashlib
import http.client

import common
import common.algorithms as alg

import connection
import connection.const.errors as c_errors

# brief: implements logic for interaction with Exmo-exchange
class Exmo():
    url = "api.exmo.com"
    api_version = "v1.1"

    def __init__(self):
        # promotion(s)
        self._taker_commission_promotion = None
        self._maker_commission_promotion = None
        # key(s)
        self._publick_key = None
        self._secret_key = None

    # brief: performs https-get/post requests to private-API of Exmo-exchange
    # param: api_method - the requested method
    # param: params - params for the specifing of the method
    # return: json-string with response from requested method
    def _QueryPrivate(self, api_method, **params):
        return self.Query(api_method, self._publick_key, self._secret_key, **params)

    # brief: creates trade-order
    # param: order_parameters - parameters for created order
    # return: json-string with response from "order_create"-method
    def _CreateOrder(self, **order_parameters):
        return common.ExecuteOrRepeat(common.Lambda(self._QueryPrivate, "order_create", **order_parameters))

    # brief: sets the publick-key for current connection
    # param: publick_key - target publick-key
    def SetPublickKey(self, publick_key):
        self._publick_key = publick_key

    # brief: sets the secret-key for current connection
    # param: publick_key - target secret-key
    def SetSecretKey(self, secret_key):
        self._secret_key = secret_key

    # NOTE: for understanding of taker and maker orders see https://info.exmo.me/ru/torgovye-vozmozhnosti/chto-takoe-sdelki-taker-maker/

    # brief: sets the promotion coefficient for taker commission
    # note1: taker promotion coefficient is the value on which taker-commission will be multiply
    # param: taker_commission_promotion - target value of taker promotion coefficient
    def SetTakerCommissionPromotion(self, taker_commission_promotion):
        self._taker_commission_promotion = taker_commission_promotion

    # brief: sets the promotion coefficient for maker commission
    # note1: maker promotion coefficient is the value on which maker-commission will be multiply
    # param: maker_commission_promotion - target value of maker promotion coefficient
    def SetMakerCommissionPromotion(self, maker_commission_promotion):
        self._maker_commission_promotion = maker_commission_promotion

    # NOTE: for detail information about all below class-methods see https://documenter.getpostman.com/view/10287440/SzYXWKPi#public_api?utm_source=site&utm_medium=articles%22

    # brief: gets information about user's account
    def GetUserInfo(self):
        return common.ExecuteOrRepeat(common.Lambda(self._QueryPrivate, "user_info"))

    def GetUserBalance(self, currency):
        return float(self.GetUserInfo()["balances"][currency])

    # brief: gets the list of user's open (active) orders
    def GetUserOpenOrders(self):
        return common.ExecuteOrRepeat(common.Lambda(self._QueryPrivate, "user_open_orders"))

    # brief: gets the list of user's candelled orders
    def GetUserCancelledOrders(self, limit=100, offset=0):
        return common.ExecuteOrRepeat(common.Lambda(self._QueryPrivate, "user_cancelled_orders", limit=limit, offset=offset))

    # brief: gets the list of user's deals
    def GetUserDeals(self, pair, limit=100, offset=0):
        return common.ExecuteOrRepeat(common.Lambda(self._QueryPrivate, "user_trades", pair=pair, limit=limit, offset=offset))

    # brief: gets the list of trade's deals
    def GetOrderDeals(self, order_id):
        last_error = None
        for _ in range(10):
            try:
                return self._QueryPrivate("order_trades", order_id=order_id)
            except c_errors.OrderIsNotFoundByID as error:
                raise error
            except c_errors.QueryError as error:
                last_error = error
        raise last_error

    # brief: creates an buy-order
    def CreateOrder_Buy(self, pair, buy_quantity, buy_rate):
        return self._CreateOrder(type="buy", pair=pair, quantity=buy_quantity, price=buy_rate)["order_id"]

    # brief: creates an buy-order at predefined total-cost
    def CreateOrder_BuyTotal(self, pair, total_cost, buy_rate):
        buy_quantity = total_cost / buy_rate
        return self._CreateOrder(type="buy", pair=pair, quantity=buy_quantity, price=buy_rate)["order_id"]

    # brief: creates an buy-order at current market buy-rate
    def CreateOrder_BuyMarket(self, pair, buy_quantity):
        return self._CreateOrder(type="market_buy", pair=pair, quantity=buy_quantity, price=0)["order_id"]

    # brief: creates an buy-order at current market buy-rate and predefined total-cost
    def CreateOrder_BuyMarketTotal(self, pair, total_cost):
        return self._CreateOrder(type="market_buy_total", pair=pair, quantity=total_cost, price=0)["order_id"]

    # brief: creates an sell-order
    def CreateOrder_Sell(self, pair, sell_quantity, sell_rate):
        return self._CreateOrder(type="sell", pair=pair, quantity=sell_quantity, price=sell_rate)["order_id"]

    # brief: creates an sell-order for selling all target currency
    # note1: if pair is "BTC_USD" the target currency is "BTC"
    def CreateOrder_SellAll(self, pair, sell_rate):
        sell_quantity = self.GetUserBalance(Exmo._1FromPair(pair))
        return self._CreateOrder(type="sell", pair=pair, quantity=sell_quantity, price=sell_rate)["order_id"]

    # brief: creates an sell-order at current market sell-rate
    def CreateOrder_SellMarket(self, pair, quantity):
        return self._CreateOrder(type="market_sell", pair=pair, quantity=quantity, price=0)["order_id"]

    # brief: creates an sell-order at current market sell-rate and predefined total-cost
    def CreateOrder_SellMarketTotal(self, pair, total_cost):
        return self._CreateOrder(type="market_sell_total", pair=pair, quantity=total_cost, price=0)["order_id"]

    # brief: cancels the trade-order by its id
    def CancelOrder(self, order_id):
        return common.ExecuteOrRepeat(common.Lambda(self._QueryPrivate, "order_cancel", order_id=order_id))

    # brief: cancels the trade-order by its id
    # note1: if a trade-order was partially executed, then the consequences of this will be eliminated
    def CancelOrderFull(self, order_id):
        try:
            order_deals = self.GetOrderDeals(order_id)
            type = order_deals["type"]
            cur1 = order_deals["in_currency"]
            cur2 = order_deals["out_currency"]
            pair = self._ToPair(cur1, cur2) if type == "buy" else self._ToPair(cur2, cur1)
            for trade in order_deals["trades"]:
                if type == "buy":
                    if self.GetCurrentSellRate(pair) > float(trade["price"]):
                        sell_quantity = float(trade["quantity"])
                        sell_quantity -= sell_quantity - float(trade["commission_amount"])
                        self.CreateOrder_SellMarket(pair, sell_quantity)
                    else:
                        error = c_errors.CannotCreateBuyOrder()
                        error.SetDescription("current sell-rate is less than buy-rate for order-deal")
                        raise error
                elif type == "sell":
                    if self.GetCurrentBuyRate(pair) < float(trade["price"]):
                        buy_cost = float(trade["amount"])
                        buy_cost -= float(trade["commission_amount"])
                        self.CreateOrder_BuyMarketTotal(pair, buy_cost)
                    else:
                        error = c_errors.CannotCreateSellOrder()
                        error.SetDescription("current buy-rate is more than sell-rate for order-deal")
                        raise error
        except c_errors.OrderIsNotFoundByID:
            pass
        return common.ExecuteOrRepeat(common.Lambda(self._QueryPrivate, "order_cancel", order_id=order_id))

    # NOTE: next below class-methods are based on upper methods

    # brief: checks is order open by its id
    # param: order_id - target trade-order id
    # return: true - if the order is open; false - vise versa
    def IsOrderOpen(self, order_id):
        for pair_orders in self.GetUserOpenOrders().values():
            for order in pair_orders:
                id = None
                try:
                    id = int(order["order_id"])
                except:
                    id = int(order["parent_order_id"])
                if id == int(order_id):
                    return True
        return False

    # brief: checks is order cancel by its id
    # param: order_id - target trade-order id
    # return: true - if the order is canceled; false - vise versa
    def IsOrderCancel(self, order_id):
        for order in self.GetUserCancelledOrders():
            id = None
            try:
                id = int(order["order_id"])
            except:
                id = int(order["parent_order_id"])
            if id == int(order_id):
                return True
        return False

    # brief: checks is order complete by its id
    # param: order_id - target trade-order id
    # return: true - if the order is completed; false - vise versa
    def IsOrderComplete(self, pair, order_id):
        for pair_orders in self.GetUserDeals(pair).values():
            for order in pair_orders:
                id = None
                try:
                    id = int(order["order_id"])
                except:
                    id = int(order["parent_order_id"])
                if id == int(order_id):
                    return True
        return False

    # brief: checking is buy-order
    # param: order_id - target trade-order id
    # return: true - if trade-order is buy-order
    def IsItBuyOrder(self, order_id):
        return self.GetOrderDeals(order_id)["type"] == "buy"

    # brief: checking is sell-order
    # param: order_id - target trade-order id
    # return: true - if trade-order is buy-order
    def IsItSellOrder(self, order_id):
        return self.GetOrderDeals(order_id)["type"] == "sell"

    # brief: gets cost of the trade-order by its id (for first currency in trade-pair)
    # note1: if trade-pair is BTC_USD the cost will given for BTC
    # param: order_id - target trade-order id
    # return: cost of the tarde-order
    def GetOrderCost1(self, order_id):
        order_deals = self.GetOrderDeals(order_id)
        if order_deals["type"] == "sell":
            return float(order_deals["out_amount"])
        elif order_deals["type"] == "buy":
            return float(order_deals["in_amount"])
        else:
            raise "unspecified type of order: {}".format(order_deals)

    # brief: gets cost of the trade-order by its id (for second currency in trade-pair)
    # note1: if trade-pair is BTC_USD the cost will given for USD
    # param: order_id - target trade-order id
    # return: cost for the trade-order
    def GetOrderCost2(self, order_id):
        order_deals = self.GetOrderDeals(order_id)
        if order_deals["type"] == "sell":
            return float(order_deals["in_amount"])
        elif order_deals["type"] == "buy":
            return float(order_deals["out_amount"])
        else:
            raise "unspecified type of order: {}".format(order_deals)

    # brief: gets rate of the trade-order by its id
    # param: order_id - target trade-order id
    # return: rate of the trade-order
    def GetOrderRate(self, order_id):
        order_deals = self.GetOrderDeals(order_id)
        in_amount = float(order_deals["in_amount"])
        out_amount = float(order_deals["out_amount"])
        if order_deals["type"] == "sell":
            return in_amount / out_amount
        elif order_deals["type"] == "buy":
            return out_amount / in_amount
        else:
            raise "unspecified type of order: {}".format(order_deals)

    # brief: gets current buy-rate for target currency-pair
    # param: pair - target currency-pair
    # return: current buy-rate
    def GetCurrentBuyRate(self, pair):
        return float(self.GetTicker()[pair]["buy_price"])

    # brief: gets current sell-rate for target currency-pair
    # param: pair - target currency-pair
    # return: current sell-rate
    def GetCurrentSellRate(self, pair):
        return float(self.GetTicker()[pair]["sell_price"])

    # brief: computes user-balance in target currency
    # param: currency - target currency
    # return: computed user-balance
    def ComputeUserBalanceIn(self, currency):
        total_balance = 0.
        user_info = self.GetUserInfo()
        free_balances = alg.RemoveFromDictIf(user_info["balances"], lambda key, value: float(value) == 0.)
        free_balances = alg.PerformForEachDict(free_balances, lambda key, value: float(value))
        reserved_balances = alg.RemoveFromDictIf(user_info["reserved"], lambda key, value: float(value) == 0.)
        reserved_balances = alg.PerformForEachDict(reserved_balances, lambda key, value: float(value))
        for balances in [free_balances, reserved_balances]:
            for real_currency, real_quantity in balances.items():
                if currency == real_currency:
                    total_balance += real_quantity
                else:
                    currency_pair = None
                    converting_rate = None
                    try:
                        currency_pair = self._ToPair(real_currency, currency)
                        converting_rate = self.GetCurrentSellRate(currency_pair)
                        commission = self.GetTakerCommission(currency_pair)
                        total_balance += real_quantity * converting_rate * commission
                    except:
                        currency_pair = self._ToPair(currency, real_currency)
                        converting_rate = self.GetCurrentBuyRate(currency_pair)
                        commission = self.GetTakerCommission(currency_pair)
                        total_balance += real_quantity / converting_rate * commission
        return total_balance

    # brief: gets commission for taker-orders
    # return: the commission value for the currency-pair like: 1.0 - if commission is 0%; 0.996 - if commission is 0.4%
    def GetTakerCommission(self, pair):
        return 1 - float(Exmo.GetPairSettings()[pair]["commission_taker_percent"]) * self._taker_commission_promotion / 100

    # brief: gets commission for maker-orders
    # return: the commission value for the currency-pair like: 1.0 - if commission is 0%; 0.996 - if commission is 0.4%
    def GetMakerCommission(self, pair):
        return 1 - float(Exmo.GetPairSettings()[pair]["commission_maker_percent"]) * self._maker_commission_promotion / 100

    # brief: gets list of the deals in currency pair
    @classmethod
    def GetTrades(cls, pair):
        return common.ExecuteOrRepeat(common.Lambda(cls.Query, "trades", pair=pair))

    # brief: gets the book of current orders on the currency pair
    @classmethod
    def GetOrderBook(cls, pair, limit=100):
        return common.ExecuteOrRepeat(common.Lambda(cls.Query, "order_book", pair=pair, limit=limit))

    # brief: gets statistics on prices and volume of trades by currency pairs
    @classmethod
    def GetTicker(cls):
        return common.ExecuteOrRepeat(common.Lambda(cls.Query, "ticker"))

    # brief: gets currency pair setting
    @classmethod
    def GetPairSettings(cls):
        return common.ExecuteOrRepeat(common.Lambda(cls.Query, "pair_settings"))

    # brief: gets avaliable list of currency
    @classmethod
    def GetCurrencyList(cls):
        return common.ExecuteOrRepeat(common.Lambda(cls.Query, "currency"))

    # brief: gets precision for computing trade-rate for the trade-pair
    # return: precision for trade-pair
    @classmethod
    def GetPricePrecisionForPair(cls, pair):
        return int(cls.GetPairSettings()[pair]["price_precision"])

    # brief: gets precision for computing trade-rate for the trade-pair
    # return: precision for trade-pair
    @classmethod
    def GetQuantityPrecisionForPair(cls, pair):
        # in Exmo-exchange quantity precision for all trade-pair is 8
        return int(8)

    # NOTE: for detailed information about structure of code in below see https://github.com/exmo-dev/exmo_api_lib/blob/master/rest/python/exmo3.py

    # brief: performs https-get/post requests to Exmo-exchange
    # param: api_method - the requested method
    # param: publick_key - the publick-key of the target user
    # param: secret_key - the private-key of the target user
    # param: params - params for the specifing of the method
    # return: json-string with response on the requested method
    @classmethod
    def Query(cls, api_method, publick_key="STUMP", secret_key=bytes("STUMP", encoding="utf-8"), **params):
        connection.Wait.WaitingGlobal(1)
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
        conn = http.client.HTTPSConnection(cls.url)
        common.ExecuteOrRepeat(common.Lambda(conn.request, "POST", "/" + cls.api_version + "/" + api_method, params, headers))
        response = conn.getresponse().read()
        conn.close()
        result = json.loads(response.decode('utf-8'))
        if "error" in result and result["error"]:
            error_message = result["error"]
            error = None
            if "Error 50304" in error_message:
                error = c_errors.OrderIsNotFoundByID()
            elif "Error 50052" in error_message:
                error = c_errors.InsufficientFundsForOrder()
            else:
                error = c_errors.QueryError()
                error.SetDescription(error_message)
            raise error
        return result

    # brief: gets first currency from currency-pair
    # return: first currency from currency-pair
    @staticmethod
    def _1FromPair(pair):
        return pair.split('_')[0]

    # brief: gets second currency from currency-pair
    # return: second currency from currency-pair
    @staticmethod
    def _2FromPair(pair):
        return pair.split('_')[1]

    # brief: creates currency-pair from two currencies
    # pram:
    @staticmethod
    def _ToPair(currency_1, currency_2):
        return "{}_{}".format(currency_1, currency_2)
