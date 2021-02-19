import trader.data_base.tables.errors as base_error

# brief: exception of not created order
class OrderIsNotCreate(base_error.SomeErrorInDB):
    def __init__(self):
        base_error.SomeErrorInDB.__init__(self)
    def __str__(self):
        return "order is not create"

# brief: exception of not available order for the trade-strategy
class NotAvailableOrderForStrategy(base_error.SomeErrorInDB):
    def __init__(self):
        base_error.SomeErrorInDB.__init__(self)
    def __str__(self):
        return "not available order for the trade-strategy"
