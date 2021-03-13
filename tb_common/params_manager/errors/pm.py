class ParametersManagerError(Exception):
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return "some error in Parameters Manager"


class ParameterIsAlreadyExist(ParametersManagerError):
    def __init__(self):
        ParametersManagerError.__init__(self)

    def __str__(self):
        return "parameter with the name is already exist"


class ParameterIsNotExist(ParametersManagerError):
    def __init__(self):
        ParametersManagerError.__init__(self)

    def __str__(self):
        return "parameter with the name is not exist"


class RequiredParameterIsNotInitialized(ParametersManagerError):
    def __init__(self):
        ParametersManagerError.__init__(self)
        self._name = ""

    def SetName(self, name):
        self._name = name

    def __str__(self):
        return "the '{}'-parameter is not initialized".format(self._name)
