import strategy.stairs as ss
import strategy.const as const
import strategy.const.errors as error

# brief: defines strategy-class by its id
# param: id - target strategy-id
# return: instance of defined strategy-class
def DefineStrategy(id):
    if id == const.ID.STAIRS_SIMPLE:
        return ss.Simple()
    elif id == const.ID.STAIRS_PROGRESSIVE_S:
        return ss.ProgressiveS()
    elif id == const.ID.FIXED_BUY_COST_S:
        return ss.FixedBuyCostS()
    elif id == const.ID.STAIRS_DEPENDENT:
        return ss.Dependency()
    elif id == const.ID.STAIRS_PROGRESSIVE_D:
        return ss.ProgressiveD()
    elif id == const.ID.FIXED_BUY_COST_D:
        return ss.FixedBuyCostD()
    else:
        raise error.UndefinedStrategyID()
