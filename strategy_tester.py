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
import os
import logging
import numpy as np


class Tester:

    def __init__(self, data_path=None, product_id=None, granularity=None):
        self.product_id = product_id
        self.granularity = granularity
        self.trade = 0  # 0 = buy, 1 = sell
        self.current = {}
        self.trades = []

        if granularity < 60:
            folder = f"{str(granularity)}m"
        elif granularity < 1440:
            folder = f"{str(int(granularity / 60))}h"
        else:
            folder = f"{str(int(granularity / (60 * 24)))}d"

        if data_path:
            self.data = pd.read_csv(data_path)
        else:
            self.data = pd.read_csv(f"refined_{folder}/{self.product_id}-refined-data.csv")

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
                self.current['entry_rsi'] = x['rsi']
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
                self.current['exit_rsi'] = x['rsi']
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

    def trades_by_month(self, month, year):
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


def find_intervals(intervals):
    df = intervals.stack().to_frame()
    df = df.reset_index(level=1)
    df.columns = ['status', 'time']
    df = df.sort_values('time')
    df['counter'] = np.nan
    df = df.reset_index().drop('index', axis=1)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')

    new_df = pd.melt(df, id_vars="time", value_name="status")
    new_df.drop(columns=["variable"], inplace=True)
    new_df['counter'] = np.where(new_df['status'].eq('start'), 1, -1).cumsum()
    new_df.to_csv("intervals.csv")
    print(new_df)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    trades = os.listdir("/Users/isaacmartinez/Desktop/TraderJoes/trades")
    granularity = 5
    expects = []
    feb_all_trades = pd.DataFrame()

    all_tests = {}

    for prod in trades:
        product_id = prod[:prod.find("trades")-1]

        logging.info(f"start testing {product_id}")
        test = Tester(product_id=product_id, granularity=granularity)
        test.test_strategy()

        logging.info(f"getting mean monthly gain percentage for {product_id}")
        index, mean = test.mean_monthly_gain_percentage()
        plt.plot(index, mean, label=product_id)

        all_tests[product_id] = test

        last_months = test.trades_by_month(2, 2024)
        last_months['product_id'] = product_id

        feb_all_trades = pd.concat([feb_all_trades, last_months[['entry_time', 'exit_time', 'product_id']]], ignore_index=True)
        ex = test.expected_period_return(last_months)
        if ex.count() > 0:
            expects.append({'product': product_id, 'return': ex.iloc[-1]})
        else:
            expects.append({'product': product_id, 'return': 100})

    plt.xlabel('years')
    plt.ylabel('mean monthly gain percentage')
    plt.legend()
    plt.show()

    logging.info("finished computing last months")

    expects = sorted(expects, key=lambda d: d['return'], reverse=True)

    last_month_top_performers = 5

    cur_expects = []

    for exp_index in expects[:last_month_top_performers]:
        logging.info(f"start testing new month for {exp_index['product']}")

        test = all_tests[exp_index['product']]
        logging.info(f"getting mean monthly gain percentage for {exp_index['product']}")
        index, mean = test.mean_monthly_gain_percentage()
        plt.plot(index, mean, label=exp_index['product'])

        current_months = test.trades_by_month(3, 2024)

        cur_ex = test.expected_period_return(current_months)

        if cur_ex.count() > 0:
            cur_expects.append({'product': exp_index['product'], 'return': cur_ex.iloc[-1]})
        else:
            cur_expects.append({'product': exp_index['product'], 'return': 100})

    plt.xlabel('years')
    plt.ylabel('mean monthly gain percentage')
    plt.legend()
    plt.show()
    feb_all_trades.to_csv("all_trades.csv")
    pd.DataFrame(expects).to_csv("february_trading.csv")
    pd.DataFrame(cur_expects).to_csv("march_trading.csv")
