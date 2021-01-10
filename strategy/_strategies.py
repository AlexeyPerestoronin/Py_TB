import strategy.stairs as ss
import strategy.const as const

def DefineStrategy(id):
    if id == const.ID.STAIRS_SIMPLE:
        return ss.Simple()
    elif id == const.ID.STAIRS_DEPENDENT:
        return ss.Dependency()
    else:
        raise "cannot define strategy by its id={}".format(id)