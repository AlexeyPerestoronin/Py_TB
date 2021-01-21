import os
import sys

sys.path.insert(0, os.getcwd())

import common
import common.faf as faf
import common.log as log

import strategy
import strategy.const as const
import strategy.const.errors as error

class Test_Srairs:
    def __init__(self, statirs, log_file_name):
        self._stairs = statirs
        self._log_file_name = os.path.join(faf.SplitPath1(sys.argv[0]), log_file_name)
        self._strategy_logger = None

    def test_Strategy(self):
        if self._stairs.IsInitialized():
            strategy.StrategyPreview(self._stairs).SavePreviewInFile(self._log_file_name)
