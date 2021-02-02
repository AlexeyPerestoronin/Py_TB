DROP TABLE "Order";
DROP TABLE "Strategy";
DROP TABLE "Trader";

-- brief: table for presenting one exchange-trader
CREATE TABLE IF NOT EXISTS "Trader"
(
id              TEXT    NOT NULL,                    -- trader identificator
status          TEXT    NOT NULL DEFAULT "void",     -- current trade-status
params          TEXT    NOT NULL,                    -- trader parameters
profit          FLOAT   NULL DEFAULT 0.0,            -- finalize profit from trading
time_start      TEXT    NULL,                        -- time of strart trading
time_stop       TEXT    NULL,                        -- time of stop trading
PRIMARY KEY("id"),
CHECK(status in ("void", "during", "finished"))
);

-- brief: table for presenting one trade-strategy
CREATE TABLE IF NOT EXISTS "Strategy"
(
id              TEXT    NOT NULL,                    -- trade-strategy identificator
id_t            TEXT    NOT NULL,                    -- identificator of master-trader
status          TEXT    NOT NULL DEFAULT "void",     -- current trade-strategy-status
recovery        TEXT    NULL,                        -- trade-strategy recovery-string
preview         TEXT    NULL,                        -- trade-strategy preview-string
profit          FLOAT   NULL DEFAULT 0.0,            -- finalize profit from trade-strategy
time_start      TEXT    NULL,                        -- time of initializing strategy
time_stop       TEXT    NULL,                        -- time of closing strategy
PRIMARY KEY("id"),
FOREIGN KEY(id_t) REFERENCES Trader(id)
CHECK(status in ("void", "init", "trade", "wait", "complete"))
);

-- brief: table for presenting one trade-order on the Exchange
CREATE TABLE IF NOT EXISTS "Order"
(
id              TEXT    NOT NULL,                    -- order identificator
id_s            TEXT    NOT NULL,                    -- identificator of master-trader
type            TEXT    NOT NULL,                    -- order type
status          TEXT    NOT NULL DEFAULT "wait",     -- order status
truview         TEXT    NULL,                        -- order truview-string
time_start      TEXT    NULL,                        -- time of opening order
time_stop       TEXT    NULL,                        -- time of closing order
PRIMARY KEY("id"),
FOREIGN KEY(id_s) REFERENCES Strategy(id),
CHECK(type in ("initial", "sell", "buy")),
CHECK(status in ("wait", "deal"))
);
