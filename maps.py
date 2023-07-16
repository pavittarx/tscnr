import MetaTrader5 as mt5

mt5tf_map = {
    "1M": mt5.TIMEFRAME_M1,
    "2M": mt5.TIMEFRAME_M2,
    "3M": mt5.TIMEFRAME_M3,
    "4M": mt5.TIMEFRAME_M4,
    "5M": mt5.TIMEFRAME_M5,
    "6M": mt5.TIMEFRAME_M6,
    "10M": mt5.TIMEFRAME_M10,
    "12M": mt5.TIMEFRAME_M12,
    "15M": mt5.TIMEFRAME_M15,
    "30M": mt5.TIMEFRAME_M30,
    "1H": mt5.TIMEFRAME_H1,
    "2H": mt5.TIMEFRAME_H2,
    "3H": mt5.TIMEFRAME_H3,
    "4H": mt5.TIMEFRAME_H4,
    "6H": mt5.TIMEFRAME_H6,
    "8H": mt5.TIMEFRAME_H8,
    "12H": mt5.TIMEFRAME_H12,
    "1D": mt5.TIMEFRAME_D1,
    "1W": mt5.TIMEFRAME_W1,
    "1MN": mt5.TIMEFRAME_MN1,
}

order_types_map = {
    # Immediate Execution w/ specified parameters (market order)
    "MARKET": mt5.TRADE_ACTION_DEAL,
    # Order with conditions (pending order)
    "LIMIT": mt5.TRADE_ACTION_PENDING,
    # Modify Stoploss & Take Profit values for opened order
    "ADD_SLTP": mt5.TRADE_ACTION_SLTP,
    # Modify parameters of previously placed order
    "MODIFY": mt5.TRADE_ACTION_MODIFY,
    # delete pending order
    "DEL_PENDING": mt5.TRADE_ACTION_REMOVE,
    # square off an opened position, (close opened order by opposite one)
    "CLOSE": mt5.TRADE_ACTION_CLOSE_BY,
}

position_type = {
    "MARKET_BUY": mt5.ORDER_TYPE_BUY,
    "MARKET_SELL": mt5.ORDER_TYPE_SELL,
    "LIMIT_BUY": mt5.ORDER_TYPE_BUY_LIMIT,
    "LIMIT_SELL": mt5.ORDER_TYPE_SELL_LIMIT,
    "LIMIT_BUY_STOP": mt5.ORDER_TYPE_BUY_STOP,
    "LIMIT_SELL_STOP": mt5.ORDER_TYPE_SELL_STOP,
    # "LIMIT_BUY_STOP_LIMIT": mt5.ORDER_TYPE_BUY_STOP_LIMIT,
    # "LIMIT_SELL_STOP_LIMIT": mt5.ORDER_TYPE_SELL_STOP_LIMIT,
    # "SQ_OFF": mt5.ORDER_TYPE_CLOSE_BY,
}

filling_type = {
    "FILL_FULL": mt5.ORDER_FILLING_FOK,
    "FILL_AVAILABLE": mt5.ORDER_FILLING_IOC,
    # "FILL_RETURN": mt5.ORDER_FILLING_RETURN
}

time_type = {
    # order stays in the queue until it is manually canceled
    "VALID_TILL_CANCELED": mt5.ORDER_TIME_GTC,
    # order is active only during the current trading day
    "VALID_DAY": mt5.ORDER_TIME_DAY,
    # order is active until the specified date
    "VALID_TIME_SPECIFIED": mt5.ORDER_TIME_SPECIFIED,
    # order is active until 23:59:59 of the specified day. If this time appears to be out of a trading session, the expiration is processed at the nearest trading time.
    "VALID_TIME_SPECIFIED_DAY": mt5.ORDER_TIME_SPECIFIED_DAY,
}
