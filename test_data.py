import http.client
import json
import requests
import csv
import time
import pandas as pd


def merge_timeframes(product_id="BTC-USD"):

    cols = ['time', 'open', 'high', 'low', 'close', 'volume']

    data_1 = pd.read_csv(f"refined_1m/{product_id}-refined-data.csv", index_col='Unnamed: 0').add_suffix("_1m")

    data_5 = pd.read_csv(f"refined_5m/{product_id}-refined-data.csv", index_col='Unnamed: 0').add_suffix("_5m")

    data_60 = pd.read_csv(f"refined_60m/{product_id}-refined-data.csv", index_col='Unnamed: 0').add_suffix("_60m")

    combined = pd.merge(data_1, data_5, left_on="time_1m", right_on="time_5m", how="left")

    #combined = pd.merge(combined, data_60, left_on="time_1m", right_on="time_60m", how="left")

    combined.to_csv("test_combine.csv")


if __name__ == '__main__':
    merge_timeframes()

