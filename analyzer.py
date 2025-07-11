import matplotlib.pyplot as plt
import os
import pandas as pd

if __name__ == "__main__":

    granularities = [1, 5, 15, 60, 60*24]

    for gran in granularities:
        if gran < 60:
            folder = f"{str(gran)}m"
        elif gran < 1440:
            folder = f"{str(int(gran / 60))}h"
        else:
            folder = f"{str(int((gran / (60 * 24))))}d"

        trades = os.listdir(f"/Users/isaacmartinez/Desktop/TraderJoes/trades_{folder}")

        all_medians = []

        for t in trades:
            data = pd.read_csv(f"trades_{folder}/{t}")
            all_medians.append((t, data['gain_percentage'].describe()['50%']))

        all_medians.sort(key=lambda x: x[1])
        print(f"for granularity {gran}")
        print(all_medians)
        print("")


