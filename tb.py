import os
import sys
import time
import json

import trader
import trader.consts as trader_const
import strategy as s
import connection as c
import common.faf as faf

def ReadSettings():
    return json.loads(faf.GetFileContent("settings.json"))

def CreateExchangeConnector(settings):
    connection_setting = settings[trader_const.SETTINGS.CONNECTION.Key]
    connector = c.Exmo()
    connector.SetPublickKey(faf.GetFileContent(connection_setting[trader_const.SETTINGS.CONNECTION.PUBLIC_KEY.Key]))
    connector.SetSecretKey(bytes(faf.GetFileContent(connection_setting[trader_const.SETTINGS.CONNECTION.SECRET_KEY.Key]), encoding="utf-8"))
    connector.SetTakerCommissionPromotion(connection_setting[trader_const.SETTINGS.CONNECTION.TAKER_COMMISSION_PROMOTION.Key])
    connector.SetMakerCommissionPromotion(connection_setting[trader_const.SETTINGS.CONNECTION.MAKER_COMMISSION_PROMOTION.Key])
    return connector

def CreateTraders(settings, connector):
    all_traders = []
    for trading_setting in settings[trader_const.SETTINGS.TRADERS.Key]:
        new_trader = trader.BuyAndSell()
        new_trader.SetConnection(connector)
        new_trader.SetParameters(trading_setting)
        all_traders.append(new_trader)
    return all_traders

def main():
    settings = ReadSettings()
    connector = CreateExchangeConnector(settings)
    traders = CreateTraders(settings, connector)
    for trader in traders:
        trader.Init()
    waiter = c.Wait(15)
    while True:
        for trader in traders:
            trader.Iterate()
        waiter.Waiting()

if __name__ == "__main__":
    main()
