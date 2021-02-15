import strategy.stairs as ss
import strategy.const as const
import strategy.const.errors as error

# brief: defines strategy-class by its id
# param: id - target strategy-id
# return: instance of defined strategy-class
def DefineStrategy(id):
    if id == const.ID.Simple:
        return ss.Simple()
    # NOTE: RC...
    elif id == const.ID.BsRcSimple:
        return ss.rate_computed.BsRcSimple()
    elif id == const.ID.BsRcDependency:
        return ss.rate_computed.BsRcDependency()
    elif id == const.ID.BsRcFixedBuyCostS:
        return ss.rate_computed.BsRcFixedBuyCostS()
    elif id == const.ID.BsRcFixedBuyCostD:
        return ss.rate_computed.BsRcFixedBuyCostD()
    elif id == const.ID.BsRcSoftCostIncreaseS:
        return ss.rate_computed.BsRcSoftCostIncreaseS()
    elif id == const.ID.BsRcSoftCostIncreaseD:
        return ss.rate_computed.BsRcSoftCostIncreaseD()
    # NOTE:CC...
    elif id == const.ID.BsCcSimple:
        return ss.cost_computed.BsCcSimple()
    elif id == const.ID.BsCcDependency:
        return ss.cost_computed.BsCcDependency()
    elif id == const.ID.BsCcDifficultDependency:
        return ss.cost_computed.BsCcDifficultDependency()
    else:
        raise error.UndefinedStrategyID()
