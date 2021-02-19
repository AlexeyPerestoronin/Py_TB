import strategy.stairs.buy_and_sell.rate_computed as ss_buy_and_sell_rate_computed
import strategy.stairs.buy_and_sell.cost_computed as ss_buy_and_sell_cost_computed
import strategy.stairs.sell_and_buy.rate_computed as ss_sell_and_buy_rate_computed

import strategy.const as const
import strategy.const.errors as error

# brief: defines strategy-class by its id
# param: id - target strategy-id
# return: instance of defined strategy-class
def DefineStrategy(id):
    if id == const.ID.StairsBase:
        raise error.UseForbiddenStrategyID()
    if id == const.ID.StairsBuySell:
        raise error.UseForbiddenStrategyID()
    if id == const.ID.StairsSellBuy:
        raise error.UseForbiddenStrategyID()
    # NOTE: buy-and-sell
    # NOTE: RC...
    elif id == const.ID.BsRcSimple:
        return ss_buy_and_sell_rate_computed.BsRcSimple()
    elif id == const.ID.BsRcDependency:
        return ss_buy_and_sell_rate_computed.BsRcDependency()
    elif id == const.ID.BsRcFixedBuyCostS:
        return ss_buy_and_sell_rate_computed.BsRcFixedBuyCostS()
    elif id == const.ID.BsRcFixedBuyCostD:
        return ss_buy_and_sell_rate_computed.BsRcFixedBuyCostD()
    elif id == const.ID.BsRcSoftCostIncreaseS:
        return ss_buy_and_sell_rate_computed.BsRcSoftCostIncreaseS()
    elif id == const.ID.BsRcSoftCostIncreaseD:
        return ss_buy_and_sell_rate_computed.BsRcSoftCostIncreaseD()
    # NOTE:CC...
    elif id == const.ID.BsCcSimple:
        return ss_buy_and_sell_cost_computed.BsCcSimple()
    elif id == const.ID.BsCcDependency:
        return ss_buy_and_sell_cost_computed.BsCcDependency()
    elif id == const.ID.BsCcDifficultDependency:
        return ss_buy_and_sell_cost_computed.BsCcDifficultDependency()
    # NOTE: sell-and-buy
    # NOTE: RC
    elif id == const.ID.SbRcSimple:
        return ss_sell_and_buy_rate_computed.SbRcSimple()
    elif id == const.ID.SbRcFixedSellQuantityS:
        return ss_sell_and_buy_rate_computed.SbRcFixedSellQuantityS()
    else:
        raise error.UndefinedStrategyID()
