import trader.data_base.tables.errors as base_error

# brief: exception of not created strategy
class StrategyIsNotCreate(base_error.SomeErrorInDB):
    def __init__(self):
        base_error.SomeErrorInDB.__init__(self)
    def __str__(self):
        return "strategy is not create"

# brief: exception of not available trade-strategy for the trader
class NotAvailableStrategyForTrader(base_error.SomeErrorInDB):
    def __init__(self):
        base_error.SomeErrorInDB.__init__(self)
    def __str__(self):
        return "not available trade-strategy for the trader"
