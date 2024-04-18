import pandas as pd
import talib as ta
import numpy as np
import math


def sigmoid_function(x):
    return 1 / (1 + math.exp(-x))


def normalize_data(data: pd.DataFrame) -> pd.DataFrame:

    data['low'] = ((data['low'] * 100) / data['low'].shift(1)) - 100
    data['high'] = ((data['high'] * 100) / data['high'].shift(1)) - 100
    data['open'] = ((data['open'] * 100) / data['open'].shift(1)) - 100
    data['close'] = ((data['close'] * 100) / data['close'].shift(1)) - 100
    data['volume'] = ((data['volume'] * 100) / data['volume'].shift(1)) - 100

    return data


def add_macd(data: pd.DataFrame, on="close") -> pd.DataFrame:
    macd, signal, histogram = ta.MACD(data[on].to_numpy())
    data['macd'] = macd
    data['signal'] = signal
    data['histogram'] = histogram
    return data


def add_rsi(data: pd.DataFrame, on='close') -> pd.DataFrame:
    data['rsi'] = ta.RSI(data[on].to_numpy())
    return data


def normalize_macd(data: pd.DataFrame) -> pd.DataFrame:
    data['macd'] = ((data['macd'] * 100) / data['macd'].shift(1)) - 100
    data['signal'] = ((data['signal'] * 100) / data['signal'].shift(1)) - 100
    data['histogram'] = ((data['histogram'] * 100) / data['histogram'].shift(1)) - 100
    return data


def normalize_rsi(data: pd.DataFrame) -> pd.DataFrame:
    data['rsi'] = ((data['rsi'] * 100) / data['rsi'].shift(1)) - 100
    return data


def trading_rules(data: pd.DataFrame) -> pd.DataFrame:
    buy = 0  # 1 = buy, 2 = sell
    def trade(x):
        nonlocal buy
        if (x['macd'] >= x['signal']) and x['macd'] <= 0 and x['signal'] <= 0 and buy == 0:
            buy = (buy + 1) % 2
            return 1
        if (x['macd'] <= x['signal']) and x['macd'] >= 0 and x['signal'] >= 0 and buy == 1:
            buy = (buy + 1) % 2
            return 2
        if x['rsi'] <= 30 and buy == 0:
            buy = (buy + 1) % 2
            return 1
        if x['rsi'] >= 70 and buy == 1:
            buy = (buy + 1) % 2
            return 2
        return 0
    trades = data.apply(trade, axis=1)
    return trades


def get_data(product: str) -> pd.DataFrame:
    return pd.read_csv(product)


def add_indicators(product_id="BTC-USD", granularity=5, on=None):

    file_name = f"data_{str(granularity)}m/{product_id}-test_data.csv"
    data_2 = get_data(file_name)

    refined_path = f"refined_{str(granularity)}m/{product_id}-refined-data.csv"

    data_2 = data_2.reindex(index=data_2.index[::-1])
    data_2 = data_2.reset_index(drop=True)
    data_2 = add_macd(data_2, on=on if on else 'close')
    data_2.to_csv(refined_path)
#


if __name__ == "__main__":
    add_indicators(granularity=1)
    add_indicators(granularity=5)
    #add_indicators(granularity=60)