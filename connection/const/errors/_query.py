from connection.const.errors import ConnectionError

# brief: base exception for query
class QueryError(ConnectionError):
    def __init__(self):
        ConnectionError.__init__(self)
    def __str__(self):
        return "some error appeared during in connection attempt: {}".format(self._description)

# brief: order is not found by its ID
class OrderIsNotFoundByID(QueryError):
    def __init__(self):
        QueryError.__init__(self)
    def __str__(self):
        return "order is not found by its ID"

# brief: insufficient funds for order
class InsufficientFundsForOrder(QueryError):
    def __init__(self):
        QueryError.__init__(self)
    def __str__(self):
        return "insufficient funds for order"
