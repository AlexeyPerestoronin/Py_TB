# brief: class for collect all exceptions that could arise in stairs-strategies
class Stairs(Exception):
    def __init__(self):
        Exception.__init__(self)
    def __str__(self):
        return "some error in stairs-trade-strategy"

# brief: some class-method in stairs-trade-strategy-class is not implemented
class MethodIsNotImplemented(Stairs):
    def __init__(self):
        Stairs.__init__(self)
    def __str__(self):
        return "some class-method in stairs-trade-strategy-class is not implemented"

# brief: exception of exceeded available currency
class ExceededAvailableCurrency(Stairs):
    def __init__(self):
        Stairs.__init__(self)
        # buy-and-sell
        self._sell_quantity = None
        self._sell_cost = None
        self._sell_rate = None
        # sell-and-buy
        self._buy_quantity = None
        self._buy_cost = None
        self._buy_rate = None

    def __str__(self):
        return "exceeded available currency for trade-strategy"

    # NOTE: buy-and-sell

    class NotSellQuantity(Stairs):
        def __init__(self):
            Stairs.__init__(self)
        def __str__(self):
            return "available currency are exceeded, but sell-quantity was not computed"

    class NotSellCost(Stairs):
        def __init__(self):
            Stairs.__init__(self)
        def __str__(self):
            return "available currency are exceeded, but sell-cost was not computed"

    class NotSellRate(Stairs):
        def __init__(self):
            Stairs.__init__(self)
        def __str__(self):
            return "available currency are exceeded, but sell-rate was not computed"

    def SetSellQuantity(self, sell_quantity):
        self._sell_quantity = sell_quantity

    def SetSellCost(self, sell_cost):
        self._sell_cost = sell_cost

    def SetSellRate(self, sell_rate):
        self._sell_rate = sell_rate

    def GetSellQuantity(self):
        if not self._sell_quantity:
            raise self.NotSellQuantity()
        return self._sell_quantity

    def GetSellCost(self):
        if not self._sell_cost:
            raise self.NotSellCost()
        return self._sell_cost

    def GetSellRate(self):
        if not self._sell_rate:
            raise self.NotSellRate()
        return self._sell_rate

    # NOTE: sell-and-buy

    class NotBuyQuantity(Stairs):
        def __init__(self):
            Stairs.__init__(self)
        def __str__(self):
            return "available currency are exceeded, but buy-quantity was not computed"

    class NotBuyCost(Stairs):
        def __init__(self):
            Stairs.__init__(self)
        def __str__(self):
            return "available currency are exceeded, but buy-cost was not computed"

    class NotBuyRate(Stairs):
        def __init__(self):
            Stairs.__init__(self)
        def __str__(self):
            return "available currency are exceeded, but buy-rate was not computed"

    def SetBuyQuantity(self, buy_quantity):
        self._buy_quantity = buy_quantity

    def SetBuyCost(self, buy_cost):
        self._buy_cost = buy_cost

    def SetBuyRate(self, buy_rate):
        self._buy_rate = buy_rate

    def GetBuyQuantity(self):
        if not self._buy_quantity:
            raise self.NotBuyQuantity()
        return self._buy_quantity

    def GetBuyCost(self):
        if not self._buy_cost:
            raise self.NotBuyCost()
        return self._buy_cost

    def GetBuyRate(self):
        if not self._buy_rate:
            raise self.NotBuyRate()
        return self._buy_rate

# brief: exception of unavailable buy-rate: buy-rate less zero
class BuyRateIsLessZero(Stairs):
    def __init__(self):
        Stairs.__init__(self)
    def __str__(self):
        return "buy-rate is less zero"

# brief: exception of unavailable buy-cost: buy-cost less zero
class BuyCostIsLessZero(Stairs):
    def __init__(self):
        Stairs.__init__(self)
    def __str__(self):
        return "buy-cost is less zero"
