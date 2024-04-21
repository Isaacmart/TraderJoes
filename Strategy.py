from get_data import *
from normalize_data import add_indicators
from strategy_tester import Tester
import pandas as pd
import threading


def parallel_testing(product_id, granularity):
    global traderDF
    print(f"start adding indicators for  {product_id}")
    add_indicators(product_id=product_id, granularity=granularity)

    refined_path = f"refined_{granularity}m/{product_id}-refined-data.csv"

    print(f"start testing {product_id}")
    test = Tester(refined_path)
    test.test_strategy()

    trades = pd.DataFrame(test.trades)
    stats = trades.describe()

    print(f"writing stats for {product_id}, \n{stats}")

    try:
        if traderDF is None:
            traderDF = stats
        else:
            traderDF = pd.concat([traderDF, stats])
    except Exception as e:
        print(e)

    print(f"writing trades for {product_id}")
    trades.to_csv(f"trades/{product_id}-trades.csv")


if __name__ == '__main__':
    traderDF = None
    products = coinbase_products()
    trade_products = []

    for product in products:
        if product['id'][-3:] == "USD" and product['trading_disabled'] is False:
            trade_products.append(product['id'])

    print(trade_products)

    ths = []

    for product in trade_products:
        print(f"starting getting data for {product}")
        coinbase_candles(product_id=product, granularity=5)
        th = threading.Thread(target=parallel_testing, args=(product, 5, ))
        th.start()
        ths.append(th)

    for th in ths:
        th.join()

    traderDF.to_csv("analysis.csv")