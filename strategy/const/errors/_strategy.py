# brief: class for collect all exceptions that could arise in strategies
class Strategy(Exception):
    def __init__(self):
        Exception.__init__(self)
    def __str__(self):
        return "some error in trade-strategy"

# brief: exception of undefined strategy
class UndefinedStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self)
    def __str__(self):
        return "strategy is undefined"

# brief: exception of undefined strategy-id
class UndefinedStrategyID(Strategy):
    def __init__(self):
        Strategy.__init__(self)
    def __str__(self):
        return "strategy-id is undefined"
