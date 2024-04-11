import http.client
import json
import requests
import csv
import time

product_id = "ETH-USD"

session = requests.session()
auth = None
api_url = 'https://api.pro.coinbase.com'
method = "get"
end_point = '/products/{}/candles'.format(product_id)
url = api_url + end_point
file_name = f"data/{product_id}-test_data.csv"

columns = ["time", "low", "high", "open", "close", "volume"]
awriter = open(file_name, "w")
writer = csv.writer(awriter, delimiter=',', quotechar='"')
writer.writerow(columns)
awriter.close()

epoch_time = int(time.time())

get_data = True
requests = 0

data = []

while requests < 9 and get_data:

    requests += 1

    current_start = epoch_time - (300 * 60)
    current_end = epoch_time

    params = {
        "start": str(current_start),
        "end": str(current_end),
        "granularity": "60"
    }

    try:
        res = session.request(method, url, params=params, auth=auth, timeout=30)
    except Exception as e:
        session = requests.session()
        continue

    if res.status_code == 200:
        res = res.json()
        data.extend(res)

        current_end = res[-1][0]
        current_start = current_end - (300 * 60)

    else:
        get_data = False
        requests = 9

    if requests >= 9:
        awriter = open(file_name, "a")
        writer = csv.writer(awriter, delimiter=',', quotechar='"')

        for line in data:
            writer.writerow(line)

        awriter.close()

        requests = 0
        data = []

