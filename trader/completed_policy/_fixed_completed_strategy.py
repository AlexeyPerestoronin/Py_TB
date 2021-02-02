import trader.completed_policy.const as const

# brief: class implements comptele-strategy-logic based of quantity of completed trade-strategies
class FixedCompletedStrategy:
    def __init__(self):
        self._available_quantity = None
        self._GetCurrentQuantity = None

    def Init(self, available_quantity, CurrentQuantityGetter):
        self._available_quantity = available_quantity
        self._GetCurrentQuantity = CurrentQuantityGetter

    def Check(self):
        return self._available_quantity > self._GetCurrentQuantity()

    @classmethod
    def GetID(cls):
        return const.IDs.FIXED_COMPLETED_STRATEGY
