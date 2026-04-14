import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.fetch_data import fetch_stock_data

data = fetch_stock_data()

print(data)