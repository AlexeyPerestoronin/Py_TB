from connection.const.errors import ConnectionError

# brief: cannot create trade-order
class CannotCreateTradeOrder(ConnectionError):
    def __init__(self):
        ConnectionError.__init__(self)
    def __str__(self):
        return "cannot create trade-order because: {}".format(self._description)

# brief: cannot create buy-order
class CannotCreateBuyOrder(CannotCreateTradeOrder):
    def __init__(self):
        CannotCreateTradeOrder.__init__(self)
    def __str__(self):
        return "cannot create buy-order because: {}".format(self._description)

# brief: cannot create sell-order
class CannotCreateSellOrder(CannotCreateTradeOrder):
    def __init__(self):
        CannotCreateTradeOrder.__init__(self)
    def __str__(self):
        return "cannot create sell-order because: {}".format(self._description)
