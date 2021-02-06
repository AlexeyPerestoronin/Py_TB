# brief: base exception for connection-classes
class ConnectionError(Exception):
    def __init__(self):
        Exception.__init__(self)
    def __str__(self):
        return "some error in connection-class"

# brief: base exception for query
class QueryError(ConnectionError):
    def __init__(self):
        ConnectionError.__init__(self)
        self._description = None

    def SetDescription(self, description):
        self._description = description

    def __str__(self):
        return "some during in connection attempt: {}".format(self._description if self._description else "not any description")

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
