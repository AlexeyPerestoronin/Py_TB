# brief: class for collect all exceptions that could arise in trader-class(es)
class Trader(Exception):
    def __init__(self):
        Exception.__init__(self)
    def __str__(self):
        return "some error in trader"

# brief: exception of undefined initial-parameter for strategy
class UndefinedInitStrategyParameter(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "undefined initial-parameter for strategy"

# brief: exception of unavailable trade-strategy for trader
class UnavailableTradeStrategyForTrader(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "unavailable trade-strategy for current trader"

# brief: exception of unavailable completed-policy for trader
class UnavailableCompletedPolicyForTrader(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "unavailable completed-policy for trader"

# brief: exception of a case when an user cancel trade-order manual
class UserCancelOrdersManual(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "a user cancel trade-orders manual"


# TODO: move to db-module

# brief: exception of not existence trader
class TraderIsNotExist(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "trader is not exist"

# brief: exception of not created trader
class TraderIsNotCreate(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "trader is not create"

# brief: exception of not created strategy
class StrategyIsNotCreate(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "strategy is not create"

# brief: exception of not created order
class OrderIsNotCreate(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "order is not create"

# brief: exception of not available trader by params
class NotAvailableTraderByParams(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "not available trader by params"


# brief: exception of not available trade-strategy for the trader
class NotAvailableStrategyForTrader(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "not available trade-strategy for the trader"

# brief: exception of not available order for the trade-strategy
class NotAvailableOrderForStrategy(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "not available order for the trade-strategy"
