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
        class QUANTITY:
            TOTAL_CLEAN = "total_clean"
            TOTAL_REAL = "total_real"
            TOTAL_LOST = "total_lost"
            TOTAL_CONCESSION = "total_concession"
        class COST:
            TOTAL_CLEAN = "total_clean"
            TOTAL_REAL = "total_real"
            TOTAL_LOST = "total_lost"
            TOTAL_CONCESSION = "total_concession"
    class STEP:
        AVAILABLE_CURRENCY = "available_currency"
        DIFFERENCE_RATE = "difference_rate"
        TOTAL_ACTIVITY_COST = "total_activity_cost"
        TOTAL_EVERAGE_AVERAGE_RATE = "total_everage_average_rate"
        SELL_RATE = "step_sell_rate"
        SELL_COST = "step_sell_cost"
        SELL_QUANTITY = "step_sell_quantity"
        BUY_RATE_0 = "buy_rate_0"
        BUY_PROFIT = "step_buy_profit"
        BUY_RATE = "step_buy_rate"
        BUY_COST = "step_buy_cost"
        BUY_QUANTITY = "step_buy_quantity"
        PROFIT_ZERO = "profit_zero"
        PROFIT_EXPECTED_LEFT = "profit_expected_left"
        PROFIT_EXPECTED_RIGHT = "profit_expected_right"
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
