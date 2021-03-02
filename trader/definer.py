import trader
import trader.consts as trader_const
import trader.errors as trader_error

# brief: identifies trader-class by its ID
# param: id - target identificator
# return: instance of identified trader-class
def DefineTrader(id):
    if trader_const.IDs.BASE_TRADER.Key == id:
        raise trader_error.UseForbiddenTraderID()
    elif trader_const.IDs.BUY_AND_SELL.Key == id:
        return trader.BuyAndSell()
    elif trader_const.IDs.SELL_AND_BUY.Key == id:
        return trader.SellAndBuy()
    else:
        raise trader_error.UndefinedTraderID()
