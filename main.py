import yfinance as yf
import pandas as pd
import numpy as np

from datetime import datetime, timedelta
import pytz

from config import timeframe, small_ema, large_ema, tickers
from sync import poller

n_candles = large_ema * 2

timeframe_secs_map = {
    "1M": 60,
    "2M": 120,
    "3M": 180,
    "4M": 240,
    "5M": 300,
    "6M": 360,
    "15M": 900,
    "30M": 1800,
    "1H": 3600,
    "4H": 14400,
    "1D": 86400,
}


def get_start_time(end_time, timeframe, n_candles):
    return end_time - timedelta(seconds=n_candles * timeframe_secs_map[timeframe])


def predict_crossover(params):
    df = params["df"]

    df["small_ema"] = df["Close"].ewm(span=small_ema, adjust=False).mean()

    df["large_ema"] = df["Close"].ewm(span=large_ema, adjust=False).mean()

    df["small_ema"] = round(df["small_ema"], params["round_factor"])
    df["large_ema"] = round(df["large_ema"], params["round_factor"])

    df["cross_diff"] = abs(df["large_ema"] - df["small_ema"])

    df["crossover_type"] = np.where(df["cross_diff"] > 0, "short", "long")

    df["crosspoint"] = np.where(df["cross_diff"] <= params["threshold"], True, False)

    print(df[-5:], "\n\n")

    def filter_signal(df):
        if (
            df["cross_diff"].iloc[-2] > df["cross_diff"].iloc[-1]
            and df["crosspoint"].iloc[-1] == True
        ):
            return True
        else:
            False

    return df[-1:] if filter_signal(df) else False


def start():
    screened = []
    for ticker in tickers:
        now = datetime.now(pytz.utc)
        start_time = get_start_time(now, timeframe, n_candles)

        print(
            "\n\n[INFO]: ",
            ticker[0],
            start_time,
            now,
            timeframe,
            small_ema,
            large_ema,
            "\n",
        )

        candles = yf.download(ticker[0], start=start_time, end=now, interval=timeframe)

        params = {
            "df": candles,
            "small_ema": small_ema,
            "large_ema": large_ema,
            "threshold": ticker[1],
            "round_factor": ticker[2],
        }

        result = predict_crossover(params)

        if result is not False:
            result["dt"] = result.index

            res = {
                "ticker": ticker[0],
                "threshold": ticker[1],
                "dt": result["dt"][0],
                "open": result["Open"][0],
                "close": result["Close"][0],
                "high": result["High"][0],
                "low": result["Low"][0],
                "small_ema": result["small_ema"][0],
                "large_ema": result["large_ema"][0],
                "cross_diff": result["cross_diff"][0],
                "_small_ema": small_ema,
                "_large_ema": large_ema,
                "_timeframe": timeframe,
            }

            screened.append(res)

    print("\nScreened Tickers: \n", pd.DataFrame(screened))


th = poller(start, timeframe, 2)
print("\n\n[INFO]: Polling started for timeframe: ", timeframe)
