import common.log as log
import common.faf as faf

import strategy.stairs as ss
import strategy.const as s_const
import strategy.const.errors as s_error

class StrategyPreview:
    def __init__(self, strategy):
        self._strategy = strategy.ComputeToStep(1)
        self._preview = "[STRATEGY-PREVIEW]\n"
        self._ResultPreviewwriter = lambda message : self.__Add(message)

    def __Add(self, string):
        self._preview += string

    def _StairsStrategyPreview(self):
        log.Logger.RegisterRecipient(repr(self), self._ResultPreviewwriter, True)
        PreviewLogger = lambda init_message: log.Logger(init_message, recipient=repr(self))
        with PreviewLogger(["Global info:", self._strategy.GetStep()]) as logger:
            key = s_const.INFO.GLOBAL
            logger.LogMessage("strategy-class is {}", repr(type(self._strategy)))
            info_global = self._strategy.GetInfo()[key]
            logger.LogInfo("increase-cost-coefficient = {}", info_global[key.COEFFICIENT])
            logger.LogInfo("total available currency  = {}", info_global[key.TOTAL_AVAILABLE_CURRENCY])
            logger.LogInfo("buy-commission            = {}", info_global[key.BUY_COMMISSION])
            logger.LogInfo("sell-commission           = {}", info_global[key.SELL_COMMISSION])
            logger.LogInfo("price precision           = {}", info_global[key.PRICE_PRECISION])
            logger.LogInfo("volume precision          = {}", info_global[key.QUANTITY_PRECISION])
            logger.LogInfo("profit                    = {}", info_global[key.PROFIT])
        is_next_step_save = True
        while is_next_step_save:
            with PreviewLogger(["Step {}:", self._strategy.GetStep()]) as logger:
                info = self._strategy.GetInfo()
                with PreviewLogger([]) as _:
                    key = s_const.INFO.GLOBAL
                    i_global = info[key]
                    with PreviewLogger("Volume:") as sub_sub_logger:
                        subkey = key.VOLUME
                        i_global_volume = i_global[subkey]
                        sub_sub_logger.LogResult("total = {}", i_global_volume[subkey.TOTAL_CLEAN])
                        sub_sub_logger.LogResult("real  = {}", i_global_volume[subkey.TOTAL_REAL])
                        sub_sub_logger.LogResult("lost  = {}", i_global_volume[subkey.TOTAL_LOST])
                    with PreviewLogger("Cost:") as sub_sub_logger:
                        subkey = key.COST
                        i_global_cost = i_global[subkey]
                        sub_sub_logger.LogResult("total = {}", i_global_cost[subkey.TOTAL_CLEAN])
                        sub_sub_logger.LogResult("real  = {}", i_global_cost[subkey.TOTAL_REAL])
                        sub_sub_logger.LogResult("lost  = {}", i_global_cost[subkey.TOTAL_LOST])
                with PreviewLogger([]) as sub_logger:
                    key = s_const.INFO.STEP
                    i_step = info[key]
                    sub_logger.LogInfo("total buy cost        = {}", i_step[key.TOTAL_BUY_COST])
                    sub_logger.LogInfo("available currency    = {}", i_step[key.AVAILABLE_CURRENCY])
                    sub_logger.LogInfo("difference rate       = {}", i_step[key.DIFFERENCE_RATE])
                    sub_logger.LogInfo("average rate          = {}", i_step[key.AVERAGE_RATE])
                    sub_logger.LogInfo("sell rate (0%-profit) = {}", i_step[key.SELL_RATE_0])
                    sub_logger.LogInfo("sell cost             = {}", i_step[key.TOTAL_SELL_COST])
                    sub_logger.LogInfo("sell profit           = {}", i_step[key.TOTAL_SELL_PROFIT])
                    sub_logger.LogInfo("sell rate             = {}", i_step[key.SELL_RATE])
                    sub_logger.LogInfo("buy ceff              = {}", i_step[key.COEFFICIENT])
                    sub_logger.LogInfo("buy cost              = {}", i_step[key.BUY_COST])
                    sub_logger.LogInfo("buy rate              = {}", i_step[key.BUY_RATE])
            try:
                self._strategy = self._strategy.ComputeNextStep()
            except s_error.ExceededAvailableCurrency as eac_error:
                with PreviewLogger(["Waiting-values for trade-strategy:", self._strategy.GetStep()]) as logger:
                    logger.LogResult("sell-quantity = {}", eac_error.GetSellQuantity())
                    logger.LogResult("sell-cost = {}", eac_error.GetSellCost())
                    logger.LogResult("sell-rate = {}", eac_error.GetSellRate())
                is_next_step_save = False
            except s_error.BuyRateIsLessZero:
                is_next_step_save = False
        log.Logger.UnregisterRecipient(repr(self))

    def GetPreview(self):
        II = lambda data_type : isinstance(self._strategy, data_type)
        if II(ss.Simple):
            self._StairsStrategyPreview()
        else:
            raise s_error.UndefinedStrategy()
        return self._preview

    def SavePreviewInFile(self, filepath):
        faf.SaveContentToFile1(filepath, self.GetPreview())