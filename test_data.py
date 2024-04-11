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
file_name = "predict_data.csv"

columns = ["time", "low", "high", "open", "close", "volume"]
awriter = open(file_name, "w")
writer = csv.writer(awriter, delimiter=',', quotechar='"')
writer.writerow(columns)
awriter.close()

epoch_time = int(1712193180)

current_start = str(epoch_time)
current_end = str(epoch_time + (300 * 60))
print(current_end)

params = {
    "start": str(current_start),
    "end": str(current_end),
    "granularity": "60"
}

res = session.request(method, url, params=params, auth=auth, timeout=30)
print(res.json())
if res.status_code == 200:
    res = res.json()

    awriter = open(file_name, "a")
    writer = csv.writer(awriter, delimiter=',', quotechar='"')

    for line in res:
        writer.writerow(line)

    awriter.close()
