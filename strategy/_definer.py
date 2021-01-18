import strategy.stairs as ss
import strategy.const as const
import strategy.const.errors as error

# brief: defines strategy-class by its id
# param: id - target strategy-id
# return: instance of defined strategy-class
def DefineStrategy(id):
    if id == const.ID.STAIRS_SIMPLE:
        return ss.Simple()
    elif id == const.ID.STAIRS_DEPENDENT:
        return ss.Dependency()
    elif id == const.ID.STAIRS_PROGRESSIVE:
        return ss.Progressive()
    else:
        raise error.UndefinedStrategyID()
