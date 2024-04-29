import http.client
import requests
import csv
import time
import logging


def coinbase_candles(product_id="BTC-USD", granularity=1, end_time=None):
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    product_id = product_id
    granularity = granularity
    session = requests.session()
    end_time = end_time

    if granularity < 60:
        folder = f"{str(granularity)}m"
    elif granularity < 1440:
        folder = f"{str(int(granularity / 60))}h"
    else:
        folder = f"{str(int((granularity / (60 * 24))))}d"

    auth = None
    api_url = 'https://api.pro.coinbase.com'
    method = "get"
    end_point = '/products/{}/candles'.format(product_id)
    url = api_url + end_point
    file_name = f"data_{folder}/{product_id}-test_data.csv"

    columns = ["time", "low", "high", "open", "close", "volume"]
    awriter = open(file_name, "w")
    writer = csv.writer(awriter, delimiter=',', quotechar='"')

    writer.writerow(columns)
    awriter.close()

    get_data = True
    reqs = 0
    data = []

    epoch_time = end_time if end_time else int(time.time())
    current_end = epoch_time
    current_start = epoch_time - (300 * (60 * granularity))

    while reqs < 9 and get_data:

        reqs += 1

        params = {
            "start": str(current_start),
            "end": str(current_end),
            "granularity": str(60 * granularity)
        }

        try:
            res = session.request(method, url, params=params, auth=auth, timeout=30)
            print(res.json())
            break
        except requests.exceptions.ReadTimeout as reRT:
            logging.info(f"exception occurred {reRT.response}")
            session = requests.session()
            res = session.request(method, url, params=params, auth=auth, timeout=30)

        if res.status_code == 200:
            #print(f"Got data from {current_start} to {current_end}")
            res = res.json()
            data.extend(res)

            try:
                current_end = res[-1][0] - (60 * granularity)
            except IndexError as ie:
                logging.info(f"error occurred {ie.args}")
                get_data = False
                reqs = 9
            current_start = current_end - (300 * (60 * granularity))

        else:
            get_data = False
            reqs = 9

        if reqs >= 9:
            awriter = open(file_name, "a")
            writer = csv.writer(awriter, delimiter=',', quotechar='"')

            for line in data:
                writer.writerow(line)

            awriter.close()

            reqs = 0
            data = []

    session.close()


def coinbase_products():

    auth = None
    session = requests.session()
    api_url = 'https://api.pro.coinbase.com'
    method = 'get'
    endpoint = '/products'
    url = api_url + endpoint
    params = ''

    res = session.request(method, url, params=params, auth=auth, timeout=30)
    return res.json()


if __name__ == "__main__":
    coinbase_candles(granularity=5)
    #products = coinbase_products()
