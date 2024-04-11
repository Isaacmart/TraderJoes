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


def add_macd(data: pd.DataFrame) -> pd.DataFrame:
    macd, signal, histogram = ta.MACD(data['close'].to_numpy())
    data['macd'] = macd
    data['signal'] = signal
    data['histogram'] = histogram

    return data


def add_rsi(data: pd.DataFrame) -> pd.DataFrame:
    data['rsi'] = ta.RSI(data['close'].to_numpy())
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


'''
data_2 = get_data("test_data.csv")
#data_2 = data_2.reindex(index=data_2.index[::-1])
#data_2 = data_2.reset_index(drop=True)
data_2 = add_macd(data_2)
data_2 = add_rsi(data_2)
data_2 = normalize_data(data_2)
data_2 = normalize_macd(data_2)
data_2 = normalize_rsi(data_2)
#data_2['trade'] = trades
data_2.to_csv('test_btc-usd.csv')
print(data_2.head(50))
'''


data_1 = get_data("test_data.csv")


data_2 = pd.concat([data_1, get_data("predict_data.csv")], ignore_index=True)
#data_2 = data_2.reindex(index=data_2.index[::-1])
#data_2 = data_2.reset_index(drop=True)
data_2 = add_macd(data_2)
data_2 = add_rsi(data_2)
data_2 = normalize_data(data_2)
data_2 = normalize_macd(data_2)
data_2 = normalize_rsi(data_2)
#data_2['trade'] = trades
data_2.to_csv('predict_btc-usd.csv')
print(data_2[data_2['time'] == 1712211180])

#