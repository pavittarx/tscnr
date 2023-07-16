from connector import MT5, get_candles_df
import pandas as pd
import numpy as np

from datetime import datetime
from decimal import *
import pytz


# parameters
# ticker, timeframe, count, small_ema, large_ema, round_factor
def get_crossover_candles(params):
    candles = MT5.get_candles(
        {
            "ticker": params["ticker"],
            "timeframe": params["timeframe"],
            "count": params["count"],
        }
    )

    df = get_candles_df(candles)

    df["small_ema"] = df["close"].ewm(span=params["small_ema"], adjust=False).mean()
    df["large_ema"] = df["close"].ewm(span=params["large_ema"], adjust=False).mean()

    df["small_ema"] = round(df["small_ema"], params["round_factor"])
    df["large_ema"] = round(df["large_ema"], params["round_factor"])

    df["cross_diff"] = df["large_ema"] - df["small_ema"]

    df["crossover_type"] = np.where(df["cross_diff"] > 0, "short", "long")

    df["diff"] = abs(df["cross_diff"])

    df["crosspoint"] = np.where(
        df["crossover_type"] != df["crossover_type"].shift(1),
        True,
        False,
    )

    return df[params["large_ema"] :]


# Paramters
# candles - candles w/ crosspoints
# thresh_index = candle index for calculating threshold
# round_factor - number of digits to round off at
def predict_threshold(params):
    df = params["candles"].copy()

    threshold_candles = []

    for i in range(0, len(df)):
        if df.iloc[i]["crosspoint"] == True:
            threshold_candles.append(df.iloc[i - params["thresh_index"]])

    freq = {}

    for candle in threshold_candles:
        diff = candle["diff"]
        key = int(round(diff, params["round_factor"]) * pow(10, params["round_factor"]))

        if key in freq:
            freq[key] = freq[key] + 1
        else:
            freq[key] = 1

    max = [0, 0]

    for key in freq:
        if freq[key] > max[1]:
            max = [key, freq[key]]

    return max[0] / pow(10, params["round_factor"])


def get_threshold_for_ticker(params):
    sym = MT5.get_tickers({"ticker": params["ticker"]})

    tick = {"ticker": sym.name, "round_factor": sym.digits}

    candles = get_crossover_candles(
        {
            "ticker": tick["ticker"],
            "timeframe": params["timeframe"],
            "count": params["count"],
            "small_ema": params["small_ema"],
            "large_ema": params["large_ema"],
            "round_factor": tick["round_factor"],
        }
    )

    threshold = predict_threshold(
        {
            "candles": candles,
            "thresh_index": params["thresh_index"],
            "round_factor": tick["round_factor"],
        }
    )

    tick["threshold"] = threshold
    tick["cross_count"] = len(candles[candles["crosspoint"] == True])

    return tick
