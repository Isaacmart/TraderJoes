"""
TO DO
1. Function that adds buy and sell flags for specific trade
2. Function that
    - calculates the return for each buy/sell pair
    - calculates rate of winning
    - calculates how much more are the winning trades than losing ones
    -
"""
import pandas as pd


class Tester:

    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        self.trade = 0  # 0 = buy, 1 = sell
        self.current = {}
        self.trades = []

    def test_strategy(self):

        self.data['shift_hist'] = self.data['histogram'].shift(1)

        def trade_longer_than(x, duration):
            return x['time'] - self.current.get('entry_time', x['time']) / 60 >= duration

        def trade_in_red(x):
            return ((x['open'] * 100) / self.current.get('entry_price', x['open'])) - 100 < 0

        def macd_strategy(x):
            if x['shift_hist'] < 0 < x['histogram'] and x['macd'] <= 0 and x['signal'] <= 0 and self.trade == 0:
                self.trade += 1
                self.current['entry_time'] = x['time']
                self.current['entry_price'] = x['open']
                self.current['entry_macd'] = x['macd']
                self.current['entry_signal'] = x['signal']
                self.current['entry_histogram'] = x['histogram']
                return 0
            elif (((x['shift_hist'] > 0 > x['histogram'] and x['macd'] >= 0 and x['signal'] >= 0)
                   or (trade_longer_than(x, 70) and trade_in_red(x)))
                  and self.trade == 1):
                self.trade -= 1
                self.current['exit_time'] = x['time']
                self.current['exit_price'] = x['open']
                self.current['exit_macd'] = x['macd']
                self.current['exit_signal'] = x['signal']
                self.current['exit_histogram'] = x['histogram']
                self.current['gain_percentage'] = ((self.current['exit_price'] * 100) / self.current['entry_price']) - 100
                self.current['duration_in_minutes'] = (self.current['exit_time'] - self.current['entry_time']) / 60
                self.trades.append(self.current)
                self.current = {}
                return 1

        self.data['trade'] = self.data.apply(macd_strategy, axis=1)


if __name__ == '__main__':
    product_id = "BTC-USD"
    granularity = 1
    refined_path = f"refined_{granularity}m/{product_id}-refined-data.csv"

    test = Tester(refined_path)
    test.test_strategy()
    trades = pd.DataFrame(test.trades)
    trades.to_csv(f"{product_id}-trades.csv")
    for column in trades.columns:
        print(column)
        print(trades[column].describe())
        print()


