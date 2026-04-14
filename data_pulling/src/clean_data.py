import pandas as pd
import os

RAW = os.path.join(os.path.dirname(__file__),
                    '..','data','raw','raw_stock_data.csv')
OUT  = os.path.join(os.path.dirname(__file__),
                    '..','data','raw','cleaned','cleaned_stock_data.csv')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def clean_stock_data():
    df = pd.read_csv(RAW)
    print(f"Raw rows: {len(df)}")

    # Fix types
    df['Date']   = pd.to_datetime(df['Date'])
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    for c in ['Open','High','Low','Close']:
        df[c] = pd.to_numeric(df[c], errors='coerce').round(2)

    # Remove problems
    print(f"Missing values:\n{df.isnull().sum()}")
    df = df.dropna()
    df = df.drop_duplicates(subset=['Ticker','Date'])
    df = df[df['Volume'] > 0]
    df = df[df['High'] >= df['Low']]

    # Add useful columns for EDA
    df = df.sort_values(['Ticker','Date']).reset_index(drop=True)
    df['Daily_Return']  = df.groupby('Ticker')['Close'].pct_change().round(4)
    df['MA7']           = df.groupby('Ticker')['Close'].transform(
                              lambda x: x.rolling(7).mean()).round(2)
    df['MA21']          = df.groupby('Ticker')['Close'].transform(
                              lambda x: x.rolling(21).mean()).round(2)
    df['Price_Range']   = (df['High'] - df['Low']).round(2)

    df.to_csv(OUT, index=False)
    print(f"Cleaned rows: {len(df)}")
    print(f"Saved to: {OUT}")
    print(df.tail(3).to_string(index=False))
    return df

if __name__ == '__main__':
    clean_stock_data()
