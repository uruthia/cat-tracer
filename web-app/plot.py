import seaborn as sns
import numpy as np
import pandas  as pd
import matplotlib as plt
import io
import base64
from pandas import Timestamp
from flask import send_file

def plot(data_anomalies, date):
    data_anomalies['day'] = data_anomalies['timestamp'].dt.day
    data_anomalies['time'] = data_anomalies['timestamp'].dt.time
    #2 grafici: uno per i rumori forti e uno per i rumori deboli
    #grafico rumori deboli
    
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(15, 10))
    sns.set_theme(style="whitegrid", fontsize = 14)
    
    ## grafico dei rumori forti nel giorno odierno
    sound_df = data_anomalies[ [data_anomalies['day'] == date,  data_anomalies['type'] == 'sound'] ]
    sns.lineplot(x="timestamp", y="value", hue="variable", data=sound_df, ax=ax1)

    heart_df = data_anomalies[ [data_anomalies['day'] == date,  data_anomalies['type'] == 'heart_rate'] ]
    sns.lineplot(x="timestamp", y="value", hue="variable", data=heart_df, ax=ax2)
    plt.savefig('static/images/plot.png')

    plt.close(fig)

