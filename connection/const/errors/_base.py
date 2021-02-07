# brief: base exception for connection-classes
class ConnectionError(Exception):
    def __init__(self):
        Exception.__init__(self)
        self._description = "unknown"

    def SetDescription(self, description):
        self._description = description

    def __str__(self):
        return "some error in connection-class because: {}".format(self._description)
