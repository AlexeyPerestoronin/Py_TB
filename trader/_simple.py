import os
import json
import copy
import time
import datetime

import common.faf as faf
import common.log as log
import strategy.const as s_const

# brief: implements simple logic for trading
class Simple:
    def __init__(self, connection, strategy):
        # settings for exchange
        self._pair = None
        # settings for trade-strategy
        self._init_cost = None
        # settings for self (for trader)
        self._connection = connection
        self._strategy = strategy
        self._DealsLogger = None
        self._ChecksLogger = None
        # setting for saving trading state
        self._save_catalog = None
        self._save_strategy = None
        self._save_trading = None
        self._log_deals = None
        self._log_actions = None
        self._log_preview = None
        # actual information about trading
        self._sell_order_id = None
        self._buy_order_id = None

    # brief: saves preview of trading-strategy that is realizing now
    def _SaveTradingPreview(self, steps_count):
        # if faf.IsFileExist1(self._log_preview):
        #     return
        copy_strategy = self._strategy.ComputeToStep(1)
        with open(self._log_preview, "w") as preview_writer:
            log.Logger.RegisterRecipient(self._log_preview, preview_writer.write, True)
            PreviewLogger = lambda init_message: log.Logger(init_message, recipient=self._log_preview)
            with PreviewLogger(["Global info:", copy_strategy.GetStep()]) as logger:
                key = s_const.INFO.GLOBAL
                info_global = copy_strategy.GetInfo()[key]
                logger.LogInfo("commission = {}", info_global[key.COMMISSION])
                logger.LogInfo("price precision = {}", info_global[key.PRICE_PRECISION])
                logger.LogInfo("volume precision = {}", info_global[key.VOLUME_PRECISION])
                logger.LogInfo("profit = {}", info_global[key.PROFIT])
                logger.LogMessage("###")
                logger.LogInfo("initial_cost = {}", self._init_cost)
                logger.LogInfo("pair = {}", self._pair)
            while copy_strategy.GetStep() < steps_count:
                with PreviewLogger(["Step {}:", copy_strategy.GetStep()]) as logger:
                    info = copy_strategy.GetInfo()
                    with PreviewLogger([]) as _:
                        key = s_const.INFO.GLOBAL
                        i_global = info[key]
                        with PreviewLogger("Volume:") as sub_sub_logger:
                            subkey = key.VOLUME
                            i_global_volume = i_global[subkey]
                            sub_sub_logger.LogResult("total = {}", i_global_volume[subkey.TOTAL_CLEAN])
                            sub_sub_logger.LogResult("real = {}", i_global_volume[subkey.TOTAL_REAL])
                            sub_sub_logger.LogResult("lost = {}", i_global_volume[subkey.TOTAL_LOST])
                        with PreviewLogger("Cost:") as sub_sub_logger:
                            subkey = key.COST
                            i_global_cost = i_global[subkey]
                            sub_sub_logger.LogResult("total = {}", i_global_cost[subkey.TOTAL_CLEAN])
                            sub_sub_logger.LogResult("real = {}", i_global_cost[subkey.TOTAL_REAL])
                            sub_sub_logger.LogResult("lost = {}", i_global_cost[subkey.TOTAL_LOST])
                    with PreviewLogger([]) as sub_logger:
                        key = s_const.INFO.STEP
                        i_step = info[key]
                        sub_logger.LogInfo("difference rate = {}", i_step[key.DIFFERENCE_RATE])
                        sub_logger.LogInfo("average price = {}", i_step[key.AVERAGE_RATE])
                        sub_logger.LogInfo("total buy cost = {}", i_step[key.TOTAL_BUY_COST])
                        sub_logger.LogInfo("sell rate for current ptofit = {}", i_step[key.SELL_RATE])
                        sub_logger.LogInfo("minimum sell rate = {}", i_step[key.SELL_RATE_0])
                        sub_logger.LogInfo("next buy rate = {}", i_step[key.NEXT_BUY_RATE])
                        sub_logger.LogInfo("next buy cost = {}", i_step[key.NEXT_BUY_COST])
                copy_strategy = copy_strategy.ComputeNextStep()
            log.Logger.UnregisterRecipient(self._log_preview)

    # brief: saves current trading state
    def _Save(self):
        self._strategy.SaveToFile(self._save_strategy)
        faf.SaveContentToFile1(self._save_trading, "{},{}".format(self._sell_order_id, self._buy_order_id))

    # brief: restores last saved trading state
    def _Restore(self):
        self._strategy = type(self._strategy).RestoreFromFile(self._save_strategy)
        file_content = faf.GetFileContent(self._save_trading).split(",")
        self._sell_order_id = int(file_content[0])
        self._buy_order_id = int(file_content[1])

    # brief: sets sell and buy orders for current step of trade-strategy
    def _SetOrders(self):
        self._sell_order_id = self._connection.CreateOrder_Sell(self._pair, self._strategy.GetSellQuantity(), self._strategy.GetSellRate())
        self._buy_order_id = self._connection.CreateOrder_BuyTotal(self._pair, self._strategy.GetBuyCost(), self._strategy.GetBuyRate())

    # brief: initializes new trading
    def _InitNewTrading(self):
        # seting first buy-order and wait while it was bought
        initial_order_id = self._connection.CreateOrder_BuyMarketTotal(self._pair, self._init_cost)
        while self._connection.IsOrderOpen(initial_order_id):
            time.sleep(30)
        initial_order_rate = self._connection.GetOrderRate(initial_order_id)
        # initializing trade-strategy on base of first buy-order metadata
        if self._strategy.GetStep():
            self._strategy = self._strategy.ComputeToStep(1)
        self._strategy.SetCommission(self._connection.GetCommissionForPair(self._pair))
        self._strategy.SetPricePrecision1(self._connection.GetPrecisionForPair(self._pair))
        self._strategy.Init(initial_order_rate, self._init_cost)
        self._SaveTradingPreview(10)
        self._SetOrders()
        self._Save()

    # brief: initializes saved trading or new, if no one saved
    def _InitTrading(self):
        if faf.IsFileExist1(self._save_strategy) and faf.IsFileExist1(self._save_trading):
            self._Restore()
            self._SaveTradingPreview(10)
        else:
            self._InitNewTrading()

    # brief: iterates initialized trading
    def _IterateTrading(self):
        trading_result = False
        is_sell_open = self._connection.IsOrderOpen(self._sell_order_id)
        is_buy_open = self._connection.IsOrderOpen(self._buy_order_id)
        if not is_sell_open and is_buy_open:
            self._connection.CancelOrder(self._buy_order_id)
            self._InitNewTrading()
            trading_result = True
        elif not is_buy_open and is_sell_open:
            self._connection.CancelOrder(self._sell_order_id)
            self._strategy = self._strategy.ComputeNextStep()
            self._SetOrders()
            self._Save()
        elif not is_buy_open and not is_sell_open:
            is_sell_complete = self._connection.IsOrderComplete(self._pair, self._sell_order_id)
            is_buy_complete = self._connection.IsOrderComplete(self._pair, self._buy_order_id)
            if is_sell_complete and is_buy_complete:
                reinitial_rate = self._connection.GetOrderRate(self._buy_order_id)
                reinitial_cost = self._strategy.GetBuyCost()
                self._strategy = self._strategy.ComputeToStep(1)
                self._strategy.Init(reinitial_rate, reinitial_cost)
                self._SaveTradingPreview(10)
                self._SetOrders()
                self._Save()
            elif is_sell_complete and not is_buy_complete:
                # TODO: there is need implement stop-trading-conditions logic
                self._InitNewTrading()
                trading_result = True
            elif is_buy_complete and not is_sell_complete:
                self._strategy = self._strategy.ComputeNextStep()
                self._SetOrders()
                self._Save()
            else:
                # in this case a user cancelled all orders manually
                trading_result = True
        return trading_result

    # brief: sets currency-pair for trading
    # param: pair - target currency-pair
    def SetPair(self, pair):
        self._pair = pair

    # brief: sets initial cost for trading
    # param: init_cost - target initial cost
    def SetInitCost(self, init_cost):
        self._init_cost = init_cost

    # brief: trading initialization
    # param: save_catalog - a catalog name in which will saving all trading's files
    def SetSaveCatalog(self, save_catalog):
        self._save_catalog = save_catalog
        faf.CreateDirectory(self._save_catalog)
        self._save_strategy = os.path.join(self._save_catalog, "strategy.save.settings.txt")
        self._save_trading = os.path.join(self._save_catalog, "trader.save.settings.txt")
        self._log_preview = os.path.join(self._save_catalog, "strategy.preview.txt")
        # TODO: need implementing log
        # self._log_deals = os.path.join(self._save_catalog, "deals.log")
        # self._log_actions = os.path.join(self._save_catalog, "actions.log")
        # log.Logger.RegisterRecipient(self._log_deals, lambda message: faf.AddContentToFile1(self._log_deals, message), True)
        # log.Logger.RegisterRecipient(self._log_actions, lambda message: faf.AddContentToFile1(self._log_actions, message), True)
        # self._DealsLogger = lambda init_message, close_message: log.Logger(init_message, close_message, recipient=self._log_deals)
        # self._ChecksLogger = lambda init_message, close_message: log.Logger(init_message, close_message, recipient=self._log_actions)

    # brief: initializing trading
    def Start(self):
        self._InitTrading()

    # brief: iterating trading
    def Iterate(self):
        self._IterateTrading()

    # brief: finishing trading
    def Finish(self):
        directory, catalogname_old = faf.SplitPath3(self._save_catalog)
        catalogname_new = catalogname_old + "-COMPLETE({})".format(datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
        faf.RenameFile(directory, catalogname_old, catalogname_new)
        return os.path.join(directory, catalogname_new)
