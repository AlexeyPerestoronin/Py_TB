import strategy.stairs as ss
import strategy.const as const
import strategy.const.errors as error

# brief: defines strategy-class by its id
# param: id - target strategy-id
# return: instance of defined strategy-class
def DefineStrategy(id):
    if id == const.ID.SIMPLE:
        return ss.Simple()
    elif id == const.ID.DEPENDENT:
        return ss.Dependency()
    elif id == const.ID.FIXED_BUY_COST_S:
        return ss.FixedBuyCostS()
    elif id == const.ID.FIXED_BUY_COST_D:
        return ss.FixedBuyCostD()
    elif id == const.ID.SOFT_COST_INCREASE_S:
        return ss.SoftCostIncreaseS()
    elif id == const.ID.SOFT_COST_INCREASE_D:
        return ss.SoftCostIncreaseD()
    else:
        raise error.UndefinedStrategyID()
