import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from strategy_tester import Tester


def best_fit(X, Y):
    xbar = sum(X) / len(X)
    print(xbar)
    ybar = sum(Y) / len(Y)
    n = len(X)  # or len(Y)

    numer = sum([xi * yi for xi, yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi ** 2 for xi in X]) - n * xbar ** 2

    b = numer / denum
    a = ybar - b * xbar

    print('best fit line:\ny = {:.2f} + {:.2f}x'.format(a, b))

    return a, b


if __name__ == "__main__":
    product_id = "BTC-USD"
    granularity = 5

    test = Tester(product_id=product_id, granularity=granularity)
    test.test_strategy()
    trades = pd.DataFrame(test.trades)
    #trades.to_csv("rsi.csv")
    #trades = test.trades_by_month(3, 2024)
    print(f"trades executed: {trades.shape}")
    print(f"expected return : {test.expected_period_return(trades).iloc[-1]}")
    print()

    trades = trades[trades['gain_percentage'] >= 0]
    print(f"trades executed: {trades.shape}")
    print(f"expected return : {test.expected_period_return(trades).iloc[-1]}")

    # solution
    a, b = best_fit(trades['entry_macd'], trades['entry_macd'])

    plt.scatter(trades['entry_macd'], trades['entry_macd'])
    yfit = [a + b * xi for xi in trades['entry_macd']]
    plt.plot(trades['entry_macd'], yfit)
    plt.show()