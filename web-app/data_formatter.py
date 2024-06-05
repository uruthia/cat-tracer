import pandas as pd
import numpy as np


def create_coordinates_dataset(list):
    print(list)
    coordinates_dataset = pd.DataFrame.from_records(list)
    # coordinates_dataset['day'] = coordinates_dataset['timestamp'].dt.date()
    # coordinates_dataset['time'] = coordinates_dataset['timestamp'].dt.time()
    return coordinates_dataset


def create_anomalies_dataset(list):
    print(list)
    anomalies_dataset = pd.DataFrame.from_records(list)
    # anomalies_dataset['day'] = anomalies_dataset['timestamp'].dt.date()
    # anomalies_dataset['time'] = anomalies_dataset['timestamp'].dt.time()
    return anomalies_dataset