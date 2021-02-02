-- SQLite
-- clear all tables
DELETE FROM "Order";
DELETE FROM "Strategy";
DELETE FROM "Trader";

-- show all tables
SELECT * FROM "Trader";
SELECT * FROM "Strategy";
SELECT * FROM "Order";

-- register new trader
-- Trader   ID-1: T-ID-1
INSERT INTO "Trader" (id, params, time_start) VALUES ("T-ID-1", "pair : 'ETH_RUB'", "21.01.2021-20:20");
SELECT id FROM "Trader" WHERE params="pair : 'ETH_RUB'";
SELECT status FROM "Trader" WHERE id="T-ID-1";
UPDATE "Trader" SET status="finished" WHERE id="T-ID-1";

SELECT profit FROM "Trader" WHERE id="T-ID-1";
UPDATE "Trader" SET profit=(1+(SELECT profit FROM "Trader" WHERE id="T-ID-1")) WHERE id="T-ID-1";
UPDATE "Trader" SET profit=NULL WHERE id="T-ID-1";
UPDATE "Trader" SET profit=1 WHERE id="T-ID-1";

-- init new trading
-- Strategy ID-1: S-ID-1
-- Order    ID-1: O-ID-1_init
INSERT INTO "Strategy" (id, id_t, time_start) VALUES ("S-ID-1", "T-ID-1", "21.01.2021-20:20");
SELECT id FROM "Strategy" WHERE id_t="T-ID-1" AND status NOT IN ("void", "complete");
SELECT status FROM "Strategy" WHERE id="S-ID-1";
SELECT profit FROM "Strategy" WHERE id="S-ID-1";
SELECT recovery FROM "Strategy" WHERE id="S-ID-1";
SELECT preview FROM "Strategy" WHERE id="S-ID-1";
UPDATE "Strategy" SET status="void" WHERE id="S-ID-1";
UPDATE "Strategy" SET time_stop="21.01.2021-21:00" WHERE id="S-ID-1";
UPDATE "Strategy" SET profit=100 WHERE id="S-ID-1";
UPDATE "Strategy" SET recovery='recovery : {}' WHERE id="S-ID-1";
UPDATE "Strategy" SET preview='preview some strategy' WHERE id="S-ID-1";

-- set-sell order (if Trader.status is "init")
-- TODO: need especialy fuction for update order as completed
INSERT INTO "Order" (id, id_s, type, time_start) VALUES ("O-ID-2_initial", "S-ID-1", "initial", "21.01.2021-20.25");
SELECT id FROM "Order" WHERE id_s="S-ID-1" AND type="initial" AND status="wait";

UPDATE "Order" SET status="deal", truview="Exmo-order-json-present", time_stop="21.01.2021-20.25" WHERE id="O-ID-2_initial";


UPDATE "Strategy" SET status="trade", id_order_S="O-ID-2_sell", WHERE id="S-ID-1";

