# brief: class collects all key-values for access to fields in launch-parameters
class Params:
    PUBLIC_KEY = "public_key"
    SECRET_KEY = "secret_key"
    TAKER_COMMISSION_PROMOTION = "taker_commission_promotion"
    MAKER_COMMISSION_PROMOTION = "maker_commission_promotion"
    class Trading:
        PAIR = "pair"
        INIT_COST = "init_cost"
        DB_FILENAME = "db_filename"
        SAVE_CATALOG = "save_catalog"
        class CompletedPolicy:
            ID = "id"
            PARAMS = "params"
        class Strategy:
            ID = "id"
            PROFIT = "profit"
            COEFFICIENT = "coefficient"
            QUANTITY_PRECISION = "quantity_precision"
            AVAILABLE_CURRENCY = "available_currency"
            DIFF_SUBCOST = "diff_subcost"
