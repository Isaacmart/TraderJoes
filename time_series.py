import http.client
import json
import requests
import csv
import time

product_id = "BTC-USD"

session = requests.session()
auth = None
api_url = 'https://api.pro.coinbase.com'
method = "get"
end_point = '/products/{}/candles'.format(product_id)
url = api_url + end_point
file_name = "test_data.csv"

columns = ["time", "low", "high", "open", "close", "volume"]
awriter = open(file_name, "w")
writer = csv.writer(awriter, delimiter=',', quotechar='"')
writer.writerow(columns)
awriter.close()

start_time = int(time.time())

get_data = True

current_start = start_time - (300 * 60)
current_end = start_time

params = {
    "start": str(current_start),
    "end": str(current_end),
    "granularity": "60"
}

res = session.request(method, url, params=params, auth=auth, timeout=30)
print(res.json())