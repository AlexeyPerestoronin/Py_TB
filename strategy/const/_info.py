class INFO:
    VALUE = "value"
    DESCRIPTION = "description"
    class GLOBAL:
        TOTAL_AVAILABLE_CURRENCY = "total_available_currency"
        BUY_COMMISSION = "buy_commission"
        SELL_COMMISSION = "sell_commission"
        PROFIT = "profit"
        PRICE_PRECISION = "price_precision"
        QUANTITY_PRECISION = "quantity_precision"
        class VOLUME:
            TOTAL_CLEAN = "total_clean"
            TOTAL_REAL = "total_real"
            TOTAL_LOST = "total_lost"
        class COST:
            TOTAL_CLEAN = "total_clean"
            TOTAL_REAL = "total_real"
            TOTAL_LOST = "total_lost"
    class STEP:
        AVAILABLE_CURRENCY = "available_currency"
        DIFFERENCE_RATE = "difference_rate"
        AVERAGE_RATE = "average_rate"
        TOTAL_BUY_COST = "total_buy_cost"
        SELL_RATE_0 = "sell_rate_0"
        SELL_PROFIT = "step_sell_profit"
        SELL_RATE = "step_sell_rate"
        SELL_COST = "step_sell_cost"
        SELL_QUANTITY = "step_sell_quantity"
        BUY_RATE = "step_buy_rate"
        BUY_COST = "step_buy_cost"
        BUY_QUANTITY = "step_buy_quantity"
        class SUBINFO:
            SUBSTEP = "substep"
            DIFF_RATE = "substep_difference_rate"
            DIFF_COST = "substep_difference_cost"
            SUBRATE_BUY_COST = "subrate_buy_cost"
            SUBRATE_BUY_RATE = "subrate_buy_rate"
            SUBRATE_BUY_QUANTITY = "subrate_buy_quantity"
            SUBRATE_SELL_COST = "subrate_sell_cost"
            SUBRATE_SELL_RATE = "subrate_sell_rate"
            SUBRATE_SELL_PROFIT = "subrate_sell_profit"
            SUBRATE_SELL_QUANTITY = "subrate_sell_quantity"
