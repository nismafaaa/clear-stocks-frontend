import pandas as pd
import os

def append_stock_to_csv(ticker: str, new_data: dict, csv_dir='data'):
    """
    Append single stock record to CSV if the date is not already present.
    Params:
        ticker (str): Stock symbol, e.g., 'AAPL'
        new_data (dict): One record of stock data, must contain 'Date'
        csv_dir (str): Folder where CSV files are stored
    """
    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, f"{ticker.lower()}_stock_price.csv")
    new_df = pd.DataFrame([new_data])

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        if new_data['Date'] in df['Date'].values:
            print(f"[SKIP] Date {new_data['Date']} already in CSV.")
            return
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = new_df

    df = df.sort_values(by='Date')
    df.to_csv(csv_path, index=False)
    print(f"[OK] Appended to {csv_path}: {new_data['Date']}")


def append_batch_to_csv(ticker: str, records: list[dict], csv_dir='data'):
    """
    Append multiple records to <ticker>_stock_price.csv, skip if already exists.
    """
    for rec in records:
        append_stock_to_csv(ticker, rec, csv_dir)
