import common

import trader.data_base.tables as table
import trader.data_base.tables.consts as table_const
import trader.data_base.tables.errors as table_error

class Order(table.Base):
    _sql = {
        "create_table" :
"""
-- brief: table for presenting one trade-order on the Exchange
CREATE TABLE IF NOT EXISTS "Order"
(
id              TEXT    NOT NULL,                    -- order identificator
id_s            TEXT    NOT NULL,                    -- identificator of master-trader
type            TEXT    NOT NULL DEFAULT "void",     -- order type
status          TEXT    NOT NULL DEFAULT "void",     -- order status
truview         TEXT    NULL,                        -- order truview-string
time_start      TEXT    NULL,                        -- time of opening order
time_stop       TEXT    NULL,                        -- time of closing order
PRIMARY KEY("id"),
FOREIGN KEY(id_s) REFERENCES Strategy(id),
CHECK(type in ("void", "initial", "sell", "buy")),
CHECK(status in ("void", "wait", "cancel", "deal"))
);
""",
        "find"          : 'SELECT id FROM "Order" WHERE id_s=?1 AND type=?2 AND status=?3;',
        "create_new"    : 'INSERT INTO "Order" (id, id_s, type, time_start) VALUES (?1, ?2, ?3, ?4);',
        "get_type"      : 'SELECT type FROM "Order" WHERE id=?1;',
        "get_status"    : 'SELECT status FROM "Order" WHERE id=?1;',
        "set_status"    : 'UPDATE "Order" SET status=?1 WHERE id=?2;',
        "set_stoptime"  : 'UPDATE "Order" SET time_stop=?1 WHERE id=?2;',
        "set_trueview"  : 'UPDATE "Order" SET truview=?1 WHERE id=?2;'
    }

    def __init__(self):
        # data-base(s)
        self._id = None
        self._type = None
        self._status = None
        self._strategy_id = None
        # callback(s)
        self._GetOrderTrueview = None

    def _SetOrderStatus(self, order_status):
        self._ExecuteOne(self._sql["set_status"], order_status, self._id)
        self._status = order_status

    def _SetOrderStoptime(self):
        if not self._id:
            raise table_error.OrderIsNotCreate()
        stoptime = self.GetDatetime()
        self._ExecuteOne(self._sql["set_stoptime"], stoptime, self._id)

    def Is(self):
        if not self._id:
            return False
        return True

    def Check(self):
        if not self._id:
            raise table_error.OrderIsNotCreate()

    # NOTE: Set...

    def SetType(self, type):
        self._type = type

    def SetStatus(self, status):
        self._status = status

    def SetStrategyId(self, strategy_id):
        self._strategy_id = strategy_id

    # NOTE: SetAs...

    def SetAsWait(self):
        self.Check()
        self._SetOrderStatus(table_const.Status.Order.WAIT)

    def SetAsDeal(self):
        self.Check()
        self._SetOrderStatus(table_const.Status.Order.DEAL)

    def SetAsCancel(self):
        self.Check()
        self._SetOrderStatus(table_const.Status.Order.CANCEL)

    # NOTE: SetCallback...

    def SetCallbackGetOrderTrueview(self, call_object):
        self._GetOrderTrueview = call_object

    # NOTE: Get...

    def GetId(self):
        self.Check()
        return self._id

    def GetType(self):
        self.Check()
        return self._ExecuteOne(self._sql["get_type"], self._id)[0][0]

    def GetStatus(self):
        self.Check()
        return self._ExecuteOne(self._sql["get_status"], self._id)[0][0]

    # NOTE: ...

    def Init(self):
        self._ExecuteOne(self._sql["create_table"])

    def Update(self):
        self.Check()
        trueview = common.TryExecute(common.Lambda(self._GetOrderTrueview, self._id))
        self._ExecuteOne(self._sql["set_trueview"], trueview, self._id)

    def Find(self):
        order_id = self._ExecuteOne(self._sql["find"], self._strategy_id, self._type, self._status)
        if not order_id:
            raise table_error.NotAvailableOrderForStrategy()
        self._id = order_id[0][0]
        self.Update()

    def Create(self, id=None):
        if not id:
            id = self.CreateId()
        self._id = id
        self._ExecuteOne(self._sql["create_new"], self._id, self._strategy_id, self._type, self.GetDatetime())
        self._status = table_const.Status.Order.WAIT
        self.SetAsWait()
        self.Update()

    def Cancel(self):
        self.Check()
        self._SetOrderStoptime()
        self.SetAsCancel()
        self.Update()
        self._id = None

    def Deal(self):
        self.Check()
        self._SetOrderStoptime()
        self.SetAsDeal()
        self.Update()
        self._id = None
