import os
import sys

sys.path.insert(0, os.getcwd())

import common
import common.faf as faf
import common.log as log
import strategy.const as const

class Test_Srairs:
    def __init__(self, statirs, log_file_name):
        self._stairs = statirs
        self._log_file_name = log_file_name

    def StepTest(self, counter):
        if counter > 0:
            CreateTestLogger = lambda init_message : log.Logger(init_message, recipient=self._log_file_name)
            with CreateTestLogger(["STEP {}", self._stairs.GetStep()]) as _:
                stairs_info = self._stairs.GetInfo()
                with CreateTestLogger("Global:") as logger:
                    key = const.INFO.GLOBAL
                    i_global = stairs_info[key]
                    # logger.LogInfo("precision = {}", i_global[key.PRECISION])
                    # logger.LogInfo("commission = {}", i_global[key.COMMISSION])
                    # logger.LogInfo("profit = {}", i_global[key.PROFIT])
                    # logger.LogInfo("step-increase-coefficient = {}", i_global[key.COEFFICIENT])
                    with CreateTestLogger("Volume:") as sublogger:
                        subkey = key.VOLUME
                        i_global_volume = i_global[subkey]
                        sublogger.LogResult("total = {}", i_global_volume[subkey.TOTAL_CLEAN])
                        sublogger.LogResult("real = {}", i_global_volume[subkey.TOTAL_REAL])
                        sublogger.LogResult("lost = {}", i_global_volume[subkey.TOTAL_LOST])
                    with CreateTestLogger("Const:") as sublogger:
                        subkey = key.COST
                        i_global_cost = i_global[subkey]
                        sublogger.LogResult("total = {}", i_global_cost[subkey.TOTAL_CLEAN])
                        sublogger.LogResult("real = {}", i_global_cost[subkey.TOTAL_REAL])
                        sublogger.LogResult("lost = {}", i_global_cost[subkey.TOTAL_LOST])
                with CreateTestLogger("Step:") as logger:
                    key = const.INFO.STEP
                    i_step = stairs_info[key]
                    logger.LogResult("difference rate = {}", i_step[key.DIFFERENCE_RATE])
                    logger.LogResult("everage price = {}", i_step[key.AVERAGE_RATE])
                    logger.LogResult("total buy cost = {}", i_step[key.TOTAL_BUY_COST])
                    logger.LogResult("sell rate for current ptofit = {}", i_step[key.SELL_RATE])
                    logger.LogResult("minimum sell rate = {}", i_step[key.SELL_RATE_0])
                    logger.LogResult("next buy rate = {}", i_step[key.NEXT_BUY_RATE])
                    logger.LogResult("next buy cost = {}", i_step[key.NEXT_BUY_COST])
                self._stairs = self._stairs.ComputeNextStep()
                self.StepTest(counter-1)

    def test_Test(self):
        with open("{}/{}".format(faf.SplitPath1(sys.argv[0]), self._log_file_name), "w") as file_writer:
            log.Logger.RegisterRecipient(self._log_file_name, file_writer.write, True)
            log.Logger.RegisterMethod(self._log_file_name, print, False)
            self.StepTest(10)
