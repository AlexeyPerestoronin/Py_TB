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
    elif id == const.ID.RCSimple:
        return ss.rate_computed.RCSimple()
    elif id == const.ID.RCDependency:
        return ss.rate_computed.RCDependency()
    elif id == const.ID.RCFixedBuyCostS:
        return ss.rate_computed.RCFixedBuyCostS()
    elif id == const.ID.RCFixedBuyCostD:
        return ss.rate_computed.RCFixedBuyCostD()
    elif id == const.ID.RCSoftCostIncreaseS:
        return ss.rate_computed.RCSoftCostIncreaseS()
    elif id == const.ID.RCSoftCostIncreaseD:
        return ss.rate_computed.RCSoftCostIncreaseD()
    # NOTE:CC...
    elif id == const.ID.CCSimple:
        return ss.cost_computed.CCSimple()
    elif id == const.ID.CCDependency:
        return ss.cost_computed.CCDependency()
    elif id == const.ID.CCDifficultDependency:
        return ss.cost_computed.CCDifficultDependency()
    else:
        raise error.UndefinedStrategyID()
