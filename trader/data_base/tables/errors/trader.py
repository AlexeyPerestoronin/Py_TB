import trader.data_base.tables.errors as base_error

# brief: exception of not available trader by params
class NotAvailableTraderByParams(base_error.SomeErrorInDB):
    def __init__(self):
        base_error.SomeErrorInDB.__init__(self)
    def __str__(self):
        return "not available trader by params"

# brief: exception of not existence trader
class TraderIsNotExist(base_error.SomeErrorInDB):
    def __init__(self):
        base_error.SomeErrorInDB.__init__(self)
    def __str__(self):
        return "trader is not exist"

# brief: exception of not created trader
class TraderIsNotCreate(base_error.SomeErrorInDB):
    def __init__(self):
        base_error.SomeErrorInDB.__init__(self)
    def __str__(self):
        return "trader is not create"
