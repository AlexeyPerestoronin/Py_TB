# brief: class for collect all exceptions that could arise in trader-class(es)
class Trader(Exception):
    def __init__(self):
        Exception.__init__(self)
    def __str__(self):
        return "some error in trader"

# brief: exception of unavailable trade-strategy for trader
class UnavailableTradeStrategyForTrader(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "unavailable trade-strategy for current trader"

# brief: exception of not available trading for continue
# note1: mostly likely it is because all tradings are completed
class NotAvailableTrading(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "not available trading for continue"
