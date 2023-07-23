import pandas as pd
import numpy as np

from datetime import datetime, timedelta
import pytz

from config import timeframe, small_ema, large_ema, tickers, candles_count, thresh_index
from connector import MT5, get_candles_df
from screener import get_threshold_for_ticker
from sync import poller

from dash import Dash, html, dash_table

app = Dash(__name__)

n_candles = large_ema * 2
timezone = pytz.utc

_tickers = []

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
    df = params["df"].copy()

    df["small_ema"] = df["close"].ewm(span=small_ema, adjust=False).mean()

    df["large_ema"] = df["close"].ewm(span=large_ema, adjust=False).mean()

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

    # return df[-1:]

    return df[-1:] if filter_signal(df) else False


screened = []


def start():
    for tick in _tickers:
        now = datetime.now(pytz.utc)
        start_time = get_start_time(now, timeframe, n_candles)

        print(
            "\n\n[INFO]: ",
            tick["ticker"],
            start_time,
            now,
            timeframe,
            small_ema,
            large_ema,
            "\n",
        )

        candles = MT5.get_candles(
            {"ticker": tick["ticker"], "timeframe": timeframe, "count": large_ema * 2}
        )

        if candles is None:
            raise Exception("No Candles Found: ", tick["ticker"])
        else:
            candles = get_candles_df(candles)

        params = {
            "df": candles,
            "small_ema": small_ema,
            "large_ema": large_ema,
            "threshold": tick["threshold"],
            "round_factor": tick["round_factor"],
        }

        result = predict_crossover(params)

        if result is not False:
            result["dt"] = result.index

            res = {
                "ticker": tick["ticker"],
                "threshold": tick["threshold"],
                "dt": result["dt"][0],
                "open": result["open"][0],
                "close": result["close"][0],
                "high": result["high"][0],
                "low": result["low"][0],
                "crossover_type": result["crossover_type"][0],
                "small_ema": result["small_ema"][0],
                "large_ema": result["large_ema"][0],
                "cross_diff": result["cross_diff"][0],
                "_small_ema": small_ema,
                "_large_ema": large_ema,
                "_timeframe": timeframe,
            }

            screened.append(res)

    screen_table = pd.DataFrame(screened)

    app.layout = html.Div(
        [
            html.H1(
                children="Screend Tickers",
                style={"textAlign": "left", "fontFamily": "sans-serif"},
            ),
            dash_table.DataTable(
                screen_table.to_dict("records"),
                [{"name": i, "id": i} for i in screen_table.columns],
                sort_action="native",
            )
            if len(screen_table)
            else html.H3(
                children="No signals so far... Please wait.",
                style={"textAlign": "left", "fontFamily": "sans-serif"},
            ),
        ]
    )


def init():
    for tick in tickers:
        _tickers.append(
            get_threshold_for_ticker(
                {
                    "ticker": tick,
                    "timeframe": timeframe,
                    "count": candles_count,
                    "thresh_index": thresh_index,
                    "small_ema": small_ema,
                    "large_ema": large_ema,
                }
            )
        )

    print("Tickers", _tickers)

    app.layout = html.Div(
        [
            html.H2(
                children="Calculating Threshold ... Please wait!",
                style={"textAlign": "left", "fontFamily": "sans-serif"},
            ),
        ]
    )

    poller(start, timeframe, 2)


print("\n\n[INFO]: Polling started for timeframe: ", timeframe)

if __name__ == "__main__":
    init()
    app.run(debug=False, port=8000)
