import trader.completed_policy.consts as const
import trader.completed_policy.errors as error

# brief: base-class for all other comptele-strategy-classes
class BaseCS:
    def __init__(self):
        self._parameters = None

    def SetAllParametersFromDict(self, params):
        raise error.MethodIsNotImplemented()

    def Init(self):
        raise error.MethodIsNotImplemented()

    def Check(self):
        raise error.MethodIsNotImplemented()

    @classmethod
    def GetID(cls):
        return const.IDs.BASE_CS.Key
