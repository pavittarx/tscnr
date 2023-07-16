import pandas as pd

from connector import MT5
from screener import get_crossover_candles, predict_threshold
from config import timeframe, small_ema, large_ema, candles_count, thresh_index

from dash import Dash, html, dash_table

app = Dash(__name__)


def start():
    symbols = MT5.get_tickers({})

    tickers = []

    for sym in symbols:
        tickers.append({"ticker": sym.name, "round_factor": sym.digits})

    for tick in tickers:
        print("Ticker", tick["ticker"], "  (", count, "/", len(tickers), ") \n")
        candles = get_crossover_candles(
            {
                "ticker": tick["ticker"],
                "timeframe": timeframe,
                "candles_count": candles_count,
                "small_ema": small_ema,
                "large_ema": large_ema,
                "round_factor": tick["round_factor"],
            }
        )

        threshold = predict_threshold(
            {
                "candles": candles,
                "thresh_index": thresh_index,
                "round_factor": tick["round_factor"],
            }
        )

        tick["threshold"] = threshold
        tick["cross_count"] = len(candles[candles["crosspoint"] == True])
        count = count + 1

    tickers = pd.DataFrame(tickers)

    app.layout = html.Div(
        [
            html.H1(
                children="Tickers Screener",
                style={"textAlign": "left", "fontFamily": "sans-serif"},
            ),
            dash_table.DataTable(
                tickers.to_dict("records"),
                [{"name": i, "id": i} for i in tickers.columns],
                sort_action="native",
            ),
        ]
    )


start()


if __name__ == "__main__":
    app.run(debug=True)
