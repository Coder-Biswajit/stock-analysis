import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta


# ================= GET STOCK DATA =================
def get_stock_data(ticker, period_days=365):
    try:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=period_days)

        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval="1d",
            auto_adjust=True
        )

        df = df.reset_index()
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

        df = df.dropna()

        # 🔹 Calculations
        df["Daily_Return"] = df["Close"].pct_change()
        df["MA7"] = df["Close"].rolling(window=7).mean()
        df["MA21"] = df["Close"].rolling(window=21).mean()
        df["Price_Range"] = df["High"] - df["Low"]

        df = df.dropna()

        return df

    except Exception as e:
        print("Error fetching data:", e)
        return None


# ================= PLOT: CLOSING PRICE =================
def plot_closing_price(df, ticker):
    try:
        os.makedirs("static/charts", exist_ok=True)

        plt.figure(figsize=(10, 5))
        plt.plot(df["Date"], df["Close"], color="blue", linewidth=1.5)

        plt.title(f"{ticker} Closing Price")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid(True)

        filename = f"static/charts/{ticker}_close.png"

        plt.savefig(filename)
        plt.close()

        return filename

    except Exception as e:
        print("Error plotting closing price:", e)
        return None


# ================= PLOT: MOVING AVERAGES =================
def plot_moving_averages(df, ticker):
    try:
        os.makedirs("static/charts", exist_ok=True)

        plt.figure(figsize=(10, 5))
        plt.plot(df["Date"], df["Close"], label="Close", linewidth=1.5)
        plt.plot(df["Date"], df["MA7"], label="MA7", linestyle="--")
        plt.plot(df["Date"], df["MA21"], label="MA21", linestyle="--")

        plt.title(f"{ticker} Moving Averages")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)

        filename = f"static/charts/{ticker}_ma.png"

        plt.savefig(filename)
        plt.close()

        return filename

    except Exception as e:
        print("Error plotting MA:", e)
        return None


# ================= PLOT: DAILY RETURNS =================
def plot_daily_returns(df, ticker):
    try:
        os.makedirs("static/charts", exist_ok=True)

        plt.figure(figsize=(8, 5))
        plt.hist(df["Daily_Return"], bins=50)

        plt.title(f"{ticker} Daily Returns")
        plt.xlabel("Return")
        plt.ylabel("Frequency")

        filename = f"static/charts/{ticker}_returns.png"

        plt.savefig(filename)
        plt.close()

        return filename

    except Exception as e:
        print("Error plotting returns:", e)
        return None


# ================= PLOT: VOLUME =================
def plot_volume(df, ticker):
    try:
        os.makedirs("static/charts", exist_ok=True)

        plt.figure(figsize=(10, 5))
        plt.bar(df["Date"], df["Volume"])

        plt.title(f"{ticker} Volume")
        plt.xlabel("Date")
        plt.ylabel("Volume")

        filename = f"static/charts/{ticker}_volume.png"

        plt.savefig(filename)
        plt.close()

        return filename

    except Exception as e:
        print("Error plotting volume:", e)
        return None


# ================= SUMMARY STATS =================
def get_summary_stats(df, ticker):
    try:
        stats = {
            "ticker": ticker,
            "current_price": round(df["Close"].iloc[-1], 2),
            "7d_return": round((df["Close"].iloc[-1] / df["Close"].iloc[-7] - 1) * 100, 2),
            "volatility": round(df["Daily_Return"].std() * 100, 2),
            "avg_volume": int(df["Volume"].mean())
        }
        return stats

    except Exception as e:
        print("Error calculating stats:", e)
        return None
    

# ================= BUY / SELL SIGNAL =================
def get_signal(df):
    try:
        latest_ma7 = df["MA7"].iloc[-1]
        latest_ma21 = df["MA21"].iloc[-1]

        if latest_ma7 > latest_ma21:
            return "Bullish 📈 (Buy Signal)"
        elif latest_ma7 < latest_ma21:
            return "Bearish 📉 (Sell Signal)"
        else:
            return "Neutral ⚖️"

    except Exception as e:
        print("Error generating signal:", e)
        return "No Signal"



# ================= TEST =================
if __name__ == "__main__":
    ticker = "RELIANCE.NS"

    df = get_stock_data(ticker)

    if df is not None:
        f1 = plot_closing_price(df, ticker)
        f2 = plot_moving_averages(df, ticker)
        f3 = plot_daily_returns(df, ticker)
        f4 = plot_volume(df, ticker)
        stats = get_summary_stats(df, ticker)

        print("Saved:", f1, f2, f3, f4)
        print("Stats:", stats)
    else:
        print("Failed to fetch data ❌")