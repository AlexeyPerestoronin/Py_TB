import os
import sys
import time
import json

import trader as t
import strategy as s
import connection as c
import common.faf as faf

def ReadSettings():
    return json.loads(faf.GetFileContent("settings.json"))

def CreateExchangeConnector(settings):
    connector = c.Exmo()
    connector.SetPublickKey(faf.GetFileContent(settings["public_key"]))
    connector.SetSecretKey(bytes(faf.GetFileContent(settings["secret_key"]), encoding="utf-8"))
    return connector

def CreateTraders(settings, connector):
    traders = []
    for trading_setting in settings["tradings"]:
        strategy = s.DefineStrategy(trading_setting["strategy"]["ID"])
        strategy.SetProfit(trading_setting["strategy"]["profit"])
        strategy.SetCoefficient(trading_setting["strategy"]["coefficient"])
        strategy.SetVolumePrecision1(trading_setting["strategy"]["volume_precision"])
        trader = t.Simple(connector, strategy)
        trader.SetPair(trading_setting["pair"])
        trader.SetInitCost(trading_setting["init_cost"])
        save_catalog = os.path.join(faf.SplitPath1(sys.argv[0]), ".trading")
        save_catalog = os.path.join(save_catalog, trading_setting["save_catalog"])
        trader.SetSaveCatalog(save_catalog)
        traders.append(trader)
    return traders

def main():
    settings = ReadSettings()
    connector = CreateExchangeConnector(settings)
    traders = CreateTraders(settings, connector)
    for trader in traders:
        trader.Start()
    while True:
        for trader in traders:
            trader.Iterate()
        time.sleep(30)

if __name__ == "__main__":
    main()