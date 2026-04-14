import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

TICKERS ={
  "RELIANCE": "RELIANCE.NS",
  "TCS":      "TCS.NS",
  "INFY":     "INFY.NS"
}
END_DATE = datetime.today().strftime('%Y-%m-%d')
START_DATE = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_stock_data():
    all_data = []
    for name, ticker in TICKERS.items():
        print(f"Fetching {name}...")
        df = yf.download(ticker, start=START_DATE, end=END_DATE,
                         interval='1d', auto_adjust=True)
        if df.empty:
            print(f"  No data for {ticker}")
            continue
        df = df.reset_index()
        df.columns = [c[0] if isinstance(c, tuple) else c
                      for c in df.columns]
        df['Ticker'] = name
        all_data.append(df)
        print(f"  Got {len(df)} rows")

    combined = pd.concat(all_data, ignore_index=True)
    combined = combined[['Ticker','Date','Open','High',
                          'Low','Close','Volume']]
    combined = combined.sort_values(['Ticker','Date'])

    out = os.path.join(OUTPUT_DIR, 'raw_stock_data.csv')
    combined.to_csv(out, index=False)
    print(f"Saved {len(combined)} rows to {out}")
    return combined

if __name__ == '__main__':
    data = fetch_stock_data()
    print(data.tail())