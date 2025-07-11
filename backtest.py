import requests
import logging
import time
import csv
import os

from datetime import datetime

run_folder = None


class DataWriter:

    def __init__(self, granularity, product_id):
        global run_folder
        if granularity < 60:
            folder = f"{str(granularity)}m"
        elif granularity < 1440:
            folder = f"{str(int(granularity / 60))}h"
        else:
            folder = f"{str(int((granularity / (60 * 24))))}d"

        if os.path.isdir(f"{run_folder}/data_{folder}") is False:
            os.mkdir(f"{run_folder}/data_{folder}")

        self.file_name = f"{run_folder}/data_{folder}/{product_id}-data.csv"

        awriter = open(self.file_name, "w")
        writer = csv.writer(awriter, delimiter=',', quotechar='"')
        columns = ["time", "low", "high", "open", "close", "volume"]
        writer.writerow(columns)
        awriter.close()

    def write(self, data):
        awriter = open(self.file_name, "a")
        writer = csv.writer(awriter, delimiter=',', quotechar='"')

        for line in data:
            writer.writerow(line)
        awriter.close()


def get_coinbase_products():
    # makes a call to the exchange to get the latest list of products
    auth = None
    session = requests.session()
    api_url = 'https://api.pro.coinbase.com'
    method = 'get'
    endpoint = '/products'
    url = api_url + endpoint
    params = ''

    res = session.request(method, url, params=params, auth=auth, timeout=30)
    return res.json()


def get_products_from_json(json_obj):
    # parses a response from the exchange to get a list of products available
    products_list = []
    for obj in json_obj:
        if obj['id'][-3:] == "USD" and obj['trading_disabled'] is False:
            products_list.append(obj['id'])
    return products_list


def get_all_candles_for_product(product):
    granularity = 1  # minute

    # network values
    auth = None
    api_url = "'https://api.exchange.coinbase.com"
    method = "get"
    end_point = '/products/{}/candles'.format(product)
    url = api_url + end_point

    epoch_time = int(time.time())
    current_end = epoch_time
    current_start = epoch_time - (300 * (60 * granularity))  # start -----------> #end -> time

    data = []
    session = requests.session()
    granularity_str = str(60 * granularity)

    data_writer = DataWriter(granularity, product)

    get_data = True  # Flag to continue getting data
    requests_made = 0
    while get_data:
        params = {
            "start": str(current_start),
            "end": str(current_end),
            "granularity": granularity_str
        }

        try:
            res = session.request(method, url, params=params, auth=auth, timeout=30)
        except requests.exceptions.ReadTimeout as reRT:
            session = requests.session()
            res = session.request(method, url, params=params, auth=auth, timeout=30)

        requests_made += 1

        if res.status_code == 200:
            res_obj = res.json()
            data.extend(res.json())

            if len(res_obj) > 0:
                current_end = res_obj[-1][0] - (60 * granularity)
                current_start = current_end - (300 * (60 * granularity))
            else:
                get_data = False

        if requests_made >= 10:
            data_writer.write(data)
            data = []
            requests_made = 0

    session.close()


if __name__ == "__main__":
    # Collects the latest data and runs the given strategy to identify product where strategy will be more successful
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    date = datetime.now()
    date_string = date.strftime("%Y-%m-%d")
    folder_name = f"data-{date_string}"

    global run_folder
    if os.path.isdir(folder_name) is False:
        os.mkdir(folder_name)
        run_folder = folder_name

    exchange_res = get_coinbase_products()

    # Data values
    product_list = get_products_from_json(exchange_res)

    for product in product_list:
        # Get data from the exchange for the product
        get_all_candles_for_product(product)





