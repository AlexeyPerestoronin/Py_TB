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

    def __init__(self):
        Stairs.__init__(self)
        self._sell_quantity = None
        self._sell_cost = None
        self._sell_rate = None

    def __str__(self):
        return "exceeded available currency for trade-strategy"

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
