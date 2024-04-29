from get_data import *
from normalize_data import add_indicators
from strategy_tester import Tester
import pandas as pd
import threading
import logging


def parallel_testing(product_id, granularity):
    global traderDF
    global logger
    logger.info(f"start adding indicators for  {product_id}")
    add_indicators(product_id=product_id, granularity=granularity)

    logger.info(f"start testing {product_id}")
    test = Tester(product_id=product_id, granularity=granularity)
    test.test_strategy()
    trades = pd.DataFrame(test.trades)
    stats = trades['gain_percentage'].describe()

    logger.info(f"writing stats for {product_id}, \n{stats}")
    traderDF = pd.concat([traderDF, stats])

    logger.info(f"writing trades for {product_id}")
    trades.to_csv(f"trades_1d/{product_id}-trades.csv")


if __name__ == '__main__':
    grans = [5, 60, 60*24]

    for gran in grans:

        traderDF = pd.DataFrame()
        products = coinbase_products()
        trade_products = []

        logger = logging.getLogger(__name__)

        logging.basicConfig(level=logging.INFO)

        for product in products:
            if product['id'][-3:] == "USD" and product['trading_disabled'] is False:
                trade_products.append(product['id'])
        logger.info(f"products: {trade_products}")

        ths = []
        for product in trade_products:
            logger.info(f"starting getting data for {product}")
            coinbase_candles(product_id=product, granularity=gran)
            th = threading.Thread(target=parallel_testing, args=(product, gran, ), name=f"{product}-thread")
            th.start()
            ths.append(th)

        for th in ths:
            th.join()

        traderDF.to_csv(f"analysis-gran{gran if gran <=60 else gran / 60}.csv")