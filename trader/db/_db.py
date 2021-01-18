import sqlite3
import datetime

import trader.const as const
import trader.const.errors as errors
import trader.db.__connection as con

# brief: implements logic of DB controlling for trader
class Simple:
    def __init__(self):
        # data-base(s)
        self._db_filepath = None
        # current trading(s)
        self._current_trading_id = None

    # brief: executes one sql-statement
    # param: sql - target sql-statement
    # param: args - arguments for filling the sql-statement
    # return: result of execution of the sql-statement
    def __ExecuteOne(self, sql, *args):
        with con.Connection(self._db_filepath) as connect:
            with connect.GetCursore() as cur:
                return cur.ExecuteOne(sql, *args)

    # brief: executes many sql-statements
    # param: sql - target sql-statement
    # param: args - arguments for filling the sql-statement
    # return: result of execution of the sql-statement
    def __ExecuteMany(self, sql, *args):
        with con.Connection(self._db_filepath) as connect:
            with connect.GetCursore() as cur:
                return cur.ExecuteMany(sql, *args)

    # brief: creates DB for trader before do business
    def _CreatesDB(self):
        self.__ExecuteOne(self._sql_tables_current_save)
        self.__ExecuteOne(self._sql_create_table_strategy_save)

    # brief: initialize BD for a trader
    # param: db_filepath - full file path to save BD
    def Init(self, db_filepath):
        self._db_filepath = db_filepath
        self._CreatesDB()
        self._current_trading_id = self.__ExecuteOne(self._sql_get_current_trading)[0][0]
        if not self._current_trading_id:
            raise errors.NotAvailableTrading()

    # brief: initialize new trading for trader
    # param: init_order_id - initial order id from which trading begins
    def InitNewTrading(self, init_order_id):
        self._current_trading_id = datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")
        self.__ExecuteOne(self._sql_init_new_trading, self._current_trading_id, init_order_id)

    # brief: checks if current trading is in init-state
    # return: true - is the trading is in init-state; false - vise versa
    def IsInit(self):
        return self.__ExecuteOne(self._sql_get_trade_status, self._current_trading_id)[0][0] == const.TraderStatus.INIT

    # brief: checks if current trading is in trade-state
    # return: true - is the trading is in trade-state; false - vise versa
    def IsTrade(self):
        return self.__ExecuteOne(self._sql_get_trade_status, self._current_trading_id)[0][0] == const.TraderStatus.TRADE

    # brief: checks if current trading is in complete-state
    # return: true - is the trading is in complete-state; false - vise versa
    def IsComplete(self):
        return self.__ExecuteOne(self._sql_get_trade_status, self._current_trading_id)[0][0] == const.TraderStatus.COMPLETE

    # brief: set current trading as completed
    def SetAsComplete(self):
        stop_trade_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")
        self.__ExecuteOne(self._sql_set_as_complete, stop_trade_datetime, self._current_trading_id)

    # brief: gets initial-order id for current trading
    # return: initial-order for the trading
    def GetInitialOrderId(self):
        return self.__ExecuteOne(self._sql_get_init_order_id, self._current_trading_id)[0][0]

    # brief: sets sell-order id for current trading
    def SetSellOrderId(self, new_sell_order_id):
        self.__ExecuteOne(self._sql_update_sell_order_id, new_sell_order_id, self._current_trading_id)

    # brief: gets current sell-order id for current trading
    # return: the sell-order for the trading
    def GetSellOrderId(self):
        return self.__ExecuteOne(self._sql_get_sell_order_id, self._current_trading_id)[0][0]

    # brief: sets buy-order id for current trading
    def SetBuyOrderId(self, new_buy_order_id):
        self.__ExecuteOne(self._sql_update_buy_order_id, new_buy_order_id, self._current_trading_id)

    # brief: gets current buy-order id for current trading
    # return: the buy-order for the trading
    def GetBuyOrderId(self):
        return self.__ExecuteOne(self._sql_get_buy_order_id, self._current_trading_id)[0][0]

    # brief: saves strategy for current trader
    # param: strategy_recovery_string - recovery string for the strategy of the trader
    def SaveStrategy(self, strategy_recovery_string):
        self.__ExecuteOne(self._sql_save_trader_strategy, self._current_trading_id, strategy_recovery_string)

    # brief: restores strategy for current trader
    # return: trade-strategy recovery string for the trader
    def RestoreStrategy(self):
        return self.__ExecuteOne(self._sql_restore_trader_strategy, self._current_trading_id)[0][0]

    _sql_tables_current_save = \
"""
CREATE TABLE IF NOT EXISTS "CurrentSave"
(
start_time 			TEXT	NOT NULL PRIMARY KEY,
stop_time			TEXT 	NULL,
initial_order_id	TEXT 	NULL,
sell_order_id 		TEXT 	NULL,
buy_order_id 		TEXT 	NULL,
is_trade 			TEXT 	NULL CHECK(is_trade in ("{0}", "{1}", "{2}")) DEFAULT "{0}"
);
""".format(const.TraderStatus.INIT, const.TraderStatus.TRADE, const.TraderStatus.COMPLETE)

    _sql_create_table_strategy_save = \
"""
CREATE TABLE IF NOT EXISTS "StrategySave"
(
id 		TEXT NOT NULL PRIMARY KEY,
storage TEXT NULL,
FOREIGN KEY(id) REFERENCES CurrentSave(start_time)
);
"""

    _sql_get_trade_status = \
"""
SELECT is_trade FROM CurrentSave WHERE start_time = ?1;
"""

    _sql_set_as_complete = \
"""
UPDATE CurrentSave SET is_trade = "{0}", stop_time = ?1 WHERE start_time = ?2;
""".format(const.TraderStatus.COMPLETE)

    _sql_init_new_trading = \
"""
INSERT INTO CurrentSave (start_time, initial_order_id) VALUES (?1, ?2);
"""

    _sql_get_current_trading = \
"""
SELECT MAX(start_time) FROM CurrentSave WHERE is_trade IN ("{0}", "{1}");
""".format(const.TraderStatus.INIT, const.TraderStatus.TRADE)

    _sql_get_init_order_id = \
"""
SELECT initial_order_id FROM CurrentSave WHERE start_time = ?1;
"""

    _sql_update_sell_order_id = \
"""
UPDATE CurrentSave SET is_trade = "{0}", sell_order_id = ?1 WHERE start_time = ?2;
""".format(const.TraderStatus.TRADE)

    _sql_get_sell_order_id = \
"""
SELECT sell_order_id FROM CurrentSave WHERE start_time = ?1;
"""

    _sql_update_buy_order_id = \
"""
UPDATE CurrentSave SET is_trade = "{0}", buy_order_id = ?1 WHERE start_time = ?2;
""".format(const.TraderStatus.TRADE)

    _sql_get_buy_order_id = \
"""
SELECT buy_order_id FROM CurrentSave WHERE start_time = ?1;
"""

    _sql_save_trader_strategy = \
"""
INSERT OR REPLACE INTO StrategySave (id, storage) VALUES (?1, ?2);
"""

    _sql_restore_trader_strategy = \
"""
SELECT storage FROM StrategySave WHERE id = ?1;
"""