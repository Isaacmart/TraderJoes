import pandas as pd


def validate_no_duplicates(product_id="BTC-USD", granularity=1):
    data = pd.read_csv(f"refined_{str(granularity)}m/{product_id}-refined-data.csv")

    return data.count() == data.drop_duplicates(subset=['time'], inplace=True).count()
