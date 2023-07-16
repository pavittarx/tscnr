from datetime import datetime
import pytz
from sync import get_current_time

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import uuid

import logging
import os
import json

from config import mt5_server, mt5_login, mt5_pass
from maps import mt5tf_map, order_types_map, position_type, filling_type, time_type


timezone = pytz.utc
mt5_path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"

connected = mt5.initialize(
    path=mt5_path, server=mt5_server, login=mt5_login, password=mt5_pass
)


def get_account_info():
    return mt5.account_info()._asdict()


def get_candles_df(candles):
    _candles = pd.DataFrame(
        candles,
        # columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'tick_volume', 'spread', 'real_volume']
    )

    _candles["Datetime"] = _candles["time"].map(
        lambda x: datetime.fromtimestamp(x, timezone)
    )

    _candles = _candles.set_index("Datetime")

    return _candles


def get_orders(**params):
    request = {}

    if "ticker" in params:
        request["symbol"] = params["ticker"]

    if "ticket" in params:
        request["ticket"] = params["ticket"]

    if "group" in params:
        request["group"] = params["group"]

    orders = mt5.orders_get(**params)

    return orders


def get_positions(**params):
    request = {}

    if "ticker" in params:
        request["symbol"] = params["ticker"]

    if "ticket" in params:
        request["ticket"] = params["ticket"]

    if "group" in params:
        request["group"] = params["group"]

    orders = mt5.orders_positions(**params)

    return orders


class MT5:
    _mt5 = mt5

    def get_candles(params):
        candles = mt5.copy_rates_from_pos(
            params["ticker"], mt5tf_map[params["timeframe"]], 0, params["count"]
        )

        utc_from = get_current_time()
        print(
            "Candles Fetched: ",
            params["ticker"],
            utc_from.strftime("%m/%d/%Y, %H:%M:%S"),
        )

        return candles

    def get_last_candle(params):
        candle = mt5.copy_rates_from_pos(
            params["ticker"], mt5tf_map[params["timeframe"]], 0, 1
        )

        candle = pd.DataFrame(candle)

        print("Candle:  ", candle.iloc[0])

        return candle.iloc[0]

    def get_orders(**params):
        request = {}

        if "ticker" in params:
            request["symbol"] = params["ticker"]

        if "ticket" in params:
            request["ticket"] = params["ticket"]

        if "group" in params:
            request["group"] = params["group"]

        orders = mt5.orders_get(**params)

        return orders

    def get_positions(**params):
        request = {}

        if "ticker" in params:
            request["symbol"] = params["ticker"]

        if "ticket" in params:
            request["ticket"] = params["ticket"]

        if "group" in params:
            request["group"] = params["group"]

        orders = mt5.positions_get(**params)

        return orders

    def place_order(params):
        id = uuid.uuid4().int & (1 << 64) - 1

        def get_order_type():
            type = params["order_type"]

            if params["trade_type"] == "short":
                type = type + "_SELL"

            if params["trade_type"] == "long":
                type = type + "_BUY"

            if "stop_order" in params and params["stop_order"]:
                type = type + "_STOP"

            if "stop_limit_order" in params and params["stop_limit_order"]:
                type = type + "_STOP_LIMIT"

            return type

        request = {
            "magic": id,
            "symbol": params["ticker"],
            "action": order_types_map[params["order_type"]],
        }

        if "trade_type" in params:
            request["type"] = position_type[get_order_type()]

        if "filling_type" in params:
            request["type_filling"] = filling_type[params["filling_type"]]

        if "time_type" in params:
            request["type_time"] = filling_type[params["time_type"]]

        if "price" in params:
            request["price"] = params["price"]

        if "lots" in params:
            request["volume"] = float(params["lots"])

        if "stoploss" in params:
            request["sl"] = params["stoploss"]

        if "takeprofit" in params:
            request["tp"] = params["takeprofit"]

        if "ticket" in params:
            request["order"] = params["ticket"]

        if "position" in params:
            request["position"] = params["position"]

        if "expire_time" in params:
            request["expiration"] = params["expire_time"]

        if "deviation" in params:
            request["deviation"] = params["deviation"]

        result = mt5.order_send(request)

        if result is None:
            print("[Log`]: Unable to add order, check provided parameters")
            print("Request:", pd.Series(request))

        result = result._asdict()

        odf = pd.DataFrame(
            {"id": id, "request": json.dumps(request), "response": json.dumps(result)},
            index=["id"],
        )

        filepath = "./dump/orders.csv"

        print("Path Exists", os.path.exists(filepath))

        if os.path.exists(filepath):
            odf.to_csv(filepath, mode="a", index=False, header=False)
        else:
            odf.to_csv(filepath, index=False, header=True)

        if result["retcode"] == 10019:
            logging.warn(f"Code [{result['retcode']}]: {result['comment']}")
            logging.warn(
                "Unable to place order. Close some positions or add some funds"
            )

        if result["retcode"] != 10009:
            logging.info(
                f"Code [{result['retcode']}]: Error while placing Order. Please try again."
            )
            logging.debug(f"\n Request \n:  {pd.Series(request)}")
            logging.debug(f"\n Response \n:  {pd.Series(result)}")

        return {
            "magic_id": id,
            "result": result if result["retcode"] == 10009 else None,
        }

    def get_tickers_count(params):
        if "group" in params:
            return mt5.symbols_get(group=params["group"])

        return mt5.symbols_total()

    def get_tickers(params):
        if "ticker" in params:
            return mt5.symbol_info(params["ticker"])

        if "group" in params:
            return mt5.symbols_get(group=params["group"])

        return mt5.symbols_get()
