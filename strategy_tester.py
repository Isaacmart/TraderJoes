"""
TO DO
1. Function that adds buy and sell flags for specific trade
2. Function that
    - calculates the return for each buy/sell pair
    - calculates rate of winning
    - calculates how much more are the winning trades than losing ones
    -
"""
import matplotlib.pyplot as plt
import pandas as pd
import datetime


class Tester:

    def __init__(self, data_path=None, product_id=None, granularity=None):
        self.product_id = product_id;
        self.granularity = granularity
        self.path = f"refined_{granularity}m/{product_id}-refined-data.csv"
        self.data = pd.read_csv(data_path) if data_path else pd.read_csv(self.path)
        self.trade = 0  # 0 = buy, 1 = sell
        self.now = ""
        self.current = {}
        self.trades = []

    def test_strategy(self):

        self.data['shift_hist'] = self.data['histogram'].shift(1)

        def trade_longer_than(x, duration):
            unix_time = unix_to_datetime(x['time'])
            return (unix_time - self.current.get('entry_time', unix_time)).total_seconds() / 60 >= duration
            #return x['time'] - self.current.get('entry_time', x['time']) / 60 >= duration

        def trade_in_red(x):
            return ((x['open'] * 100) / self.current.get('entry_price', x['open'])) - 100 < 0

        def unix_to_datetime(unix_time):
            return datetime.datetime.fromtimestamp(unix_time)

        def macd_strategy(x):

            if (x['shift_hist'] < 0 < x['histogram']
                    and x['macd'] <= 0 and x['signal'] <= 0
                    and self.trade == 0):
                self.current['entry_time'] = unix_to_datetime(x['time'])
                self.current['entry_price'] = x['open']
                self.current['entry_macd'] = x['macd']
                self.current['entry_signal'] = x['signal']
                self.current['entry_histogram'] = x['histogram']
                self.trade += 1
                return 0

            if (((x['shift_hist'] > 0 > x['histogram'] and x['macd'] >= 0 and x['signal'] >= 0)
                    or (trade_longer_than(x, 70) and trade_in_red(x)))
                    and self.trade == 1):
                self.current['exit_time'] = unix_to_datetime(x['time'])
                self.current['exit_price'] = x['open']
                self.current['exit_macd'] = x['macd']
                self.current['exit_signal'] = x['signal']
                self.current['exit_histogram'] = x['histogram']
                self.current['gain_percentage'] = ((self.current['exit_price'] * 100) / self.current['entry_price']) - 100
                self.current['duration_in_minutes'] = (self.current['exit_time'] - self.current['entry_time']).total_seconds() / 60
                self.trades.append(self.current)
                self.trade -= 1
                self.current = {}
                return 1

        self.data['trade'] = self.data.apply(macd_strategy, axis=1)

    def save(self):
        trades = pd.DataFrame(self.trades)
        trades.to_csv(f"{self.product_id}-trades.csv")

    def mean_monthly_gain_percentage(self):
        trades = pd.DataFrame(self.trades)
        trades['entry_time'] = pd.to_datetime(trades['entry_time'], format='%d.%m.%Y %H:%M:%S')
        trade_groups = trades.groupby(pd.Grouper(key="entry_time", freq="m"))
        #trade_groups['gain_percentage'].describe().to_csv(f"{self.product_id}-groups.csv")
        gain_percentage_describe = trade_groups['gain_percentage'].describe()
        return gain_percentage_describe.index, gain_percentage_describe['mean']

    def save_trades_by_month(self, month, year):
        trades = pd.DataFrame(self.trades)
        trades['entry_time'] = pd.to_datetime(trades['entry_time'], format='%d.%m.%Y %H:%M:%S')
        return trades[(trades['entry_time'].dt.month == month) & (trades['entry_time'].dt.year == year)]
        #tmp.to_csv(f"{self.product_id}-{str(month)}-{str(year)}-trades.csv")

    def expected_period_return(self, data=None, start_cap=100):
        period = data if data is not None else pd.DataFrame(self.trades)
        res = start_cap

        def helper(x):
            nonlocal res
            res = tmp = res * (1 + (x['gain_percentage'] / 100))
            return tmp

        return period.apply(helper, axis=1)


if __name__ == '__main__':
    product_id = "RARE-USD"
    granularity = 5
    refined_path = f"refined_{granularity}m/{product_id}-refined-data.csv"

    test = Tester(product_id=product_id, granularity=granularity)
    test.test_strategy()
    test.save()
    #test.mean_monthly_gain_percentage()
    #test.save_trades_by_month(8, 2023)
    test.expected_period_return()


