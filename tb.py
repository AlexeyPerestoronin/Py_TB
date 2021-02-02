import os
import sys
import time
import json

import trader as t
import trader.const as t_const
import strategy as s
import connection as c
import common.faf as faf

def ReadSettings():
    return json.loads(faf.GetFileContent("settings.json"))

def CreateExchangeConnector(settings):
    connector = c.Exmo()
    connector.SetPublickKey(faf.GetFileContent(settings[t_const.Params.PUBLIC_KEY]))
    connector.SetSecretKey(bytes(faf.GetFileContent(settings[t_const.Params.SECRET_KEY]), encoding="utf-8"))
    connector.SetTakerCommissionPromotion(settings[t_const.Params.TAKER_COMMISSION_PROMOTION])
    connector.SetMakerCommissionPromotion(settings[t_const.Params.MAKER_COMMISSION_PROMOTION])
    return connector

def CreateTraders(settings, connector):
    traders = []
    for trading_setting in settings["tradings"]:
        trader = t.Simple()
        trader.SetConnection(connector)
        trader.SetParameters(trading_setting)
        traders.append(trader)
    return traders

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
