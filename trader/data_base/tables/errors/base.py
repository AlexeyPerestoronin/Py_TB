import trader.errors as t_error

# brief: some error in trader by db-submodule reason
class SomeErrorInDB(t_error.Trader):
    def __init__(self):
        t_error.Trader.__init__(self)
    def __str__(self):
        return "some error in trader by db-submodule reason"