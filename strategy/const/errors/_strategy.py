class SomeErrorInTradeStrategy(Exception):
    def __init__(self):
        Exception.__init__(self)
    def __str__(self):
        return "some error in trade-strategy"

class NotInitializedStrategy(SomeErrorInTradeStrategy):
    def __init__(self):
        SomeErrorInTradeStrategy.__init__(self)
    def __str__(self):
        return "strategy is not initialized"

class UndefinedStrategy(SomeErrorInTradeStrategy):
    def __init__(self):
        SomeErrorInTradeStrategy.__init__(self)
    def __str__(self):
        return "strategy is undefined"

class UseForbiddenStrategyID(SomeErrorInTradeStrategy):
    def __init__(self):
        SomeErrorInTradeStrategy.__init__(self)
    def __str__(self):
        return "strategy-id is forbidden to use"

class UndefinedStrategyID(SomeErrorInTradeStrategy):
    def __init__(self):
        SomeErrorInTradeStrategy.__init__(self)
    def __str__(self):
        return "strategy-id is undefined"
