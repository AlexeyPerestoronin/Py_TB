import os
import sys

sys.path.insert(0, os.getcwd())

import common
import common.faf as faf
import common.log as log
import strategy.const as const
import strategy.const.errors as error

class Test_Srairs:
    def __init__(self, statirs, log_file_name):
        self._stairs = statirs
        self._log_file_name = log_file_name
        self._strategy_logger = None

    def _LogStep(self):
        with self._strategy_logger(["STEP {}", self._stairs.GetStep()]) as _:
            stairs_info = self._stairs.GetInfo()
            with self._strategy_logger("Global:") as logger:
                key = const.INFO.GLOBAL
                i_global = stairs_info[key]
                with self._strategy_logger("Volume:") as sublogger:
                    subkey = key.VOLUME
                    i_global_volume = i_global[subkey]
                    sublogger.LogResult("total = {}", i_global_volume[subkey.TOTAL_CLEAN])
                    sublogger.LogResult("real = {}", i_global_volume[subkey.TOTAL_REAL])
                    sublogger.LogResult("lost = {}", i_global_volume[subkey.TOTAL_LOST])
                with self._strategy_logger("Cost:") as sublogger:
                    subkey = key.COST
                    i_global_cost = i_global[subkey]
                    sublogger.LogResult("total = {}", i_global_cost[subkey.TOTAL_CLEAN])
                    sublogger.LogResult("real = {}", i_global_cost[subkey.TOTAL_REAL])
                    sublogger.LogResult("lost = {}", i_global_cost[subkey.TOTAL_LOST])
            with self._strategy_logger("Step:") as logger:
                key = const.INFO.STEP
                i_step = stairs_info[key]
                logger.LogResult("difference rate = {}", i_step[key.DIFFERENCE_RATE])
                logger.LogResult("everage price = {}", i_step[key.AVERAGE_RATE])
                logger.LogResult("total buy-cost = {}", i_step[key.TOTAL_BUY_COST])
                logger.LogResult("sell rate for current ptofit = {}", i_step[key.SELL_RATE])
                logger.LogResult("total sell-cost = {}", i_step[key.TOTAL_SELL_COST])
                logger.LogResult("minimum sell rate = {}", i_step[key.SELL_RATE_0])
                logger.LogResult("next buy rate = {}", i_step[key.NEXT_BUY_RATE])
                logger.LogResult("next buy cost = {}", i_step[key.NEXT_BUY_COST])
        try:
            self._stairs = self._stairs.ComputeNextStep()
            self._LogStep()
        except error.ExceededAvailableCurrency:
            pass
        return

    def test_Strategy(self):
        with open("{}/{}".format(faf.SplitPath1(sys.argv[0]), self._log_file_name), "w") as file_writer:
            log.Logger.RegisterRecipient(self._log_file_name, file_writer.write, True)
            log.Logger.RegisterMethod(self._log_file_name, print, False)
            self._strategy_logger = lambda init_message : log.Logger(init_message, recipient=self._log_file_name)
            with self._strategy_logger("Global:") as logger:
                key = const.INFO.GLOBAL
                i_global = self._stairs.GetInfo()[key]
                logger.LogInfo("buy-commission = {}", i_global[key.BUY_COMMISSION])
                logger.LogInfo("sell-commission = {}", i_global[key.SELL_COMMISSION])
                logger.LogInfo("price-precision = {}", i_global[key.PRICE_PRECISION])
                logger.LogInfo("volume-precision = {}", i_global[key.QUANTITY_PRECISION])
                logger.LogInfo("profit = {}", i_global[key.PROFIT])
                logger.LogInfo("step-increase-coefficient = {}", i_global[key.COEFFICIENT])
            self._LogStep()
