class Trader(Exception):
    def __init__(self):
        Exception.__init__(self)
    def __str__(self):
        return "some error in trader"

class MethodIsNotImplemented(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "some method is not implemented for the trader-class"

class UndefinedInitStrategyParameter(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "undefined initial-parameter for strategy"

class UnavailableTradeStrategyForTrader(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "unavailable trade-strategy for current trader"

class UnavailableCompletedPolicyForTrader(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "unavailable completed-policy for trader"

class UserCancelOrdersManual(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "a user cancel trade-orders manual"

class UseForbiddenTraderID(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "the trader-class is forbidden to use"

class UndefinedTraderID(Trader):
    def __init__(self):
        Trader.__init__(self)
    def __str__(self):
        return "undefined trader id"
