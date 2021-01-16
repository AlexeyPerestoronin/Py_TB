# brief: class for collect all exceptions that could arise in stairs-strategies
class Stairs(Exception):
    def __init__(self):
        Exception.__init__(self)
    def __str__(self):
        return "some error in stairs-trade-strategy"

# brief: exception of exceeded available currency
class ExceededAvailableCurrency(Stairs):
    def __init__(self):
        Stairs.__init__(self)
    def __str__(self):
        return "exceeded available currency for trade-strategy"
