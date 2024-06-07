from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials, firestore
import folium
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64
import data_formatter
import pandas as pd
import plot

app = Flask(__name__)
socketio = SocketIO(app)

# Inizializzazione di Firebase
cred = credentials.Certificate('service_account_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
coordinates_dataset = pd.DataFrame()
anomalies_dataset = pd.DataFrame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map') # lat long type value
def map_view():
    
    coordinates_list = [[46.100, 13.262]]  # Coordinate di default

    # Utilizza la prima coppia di coordinate per centrare la mappa
    folium_map = folium.Map(location=coordinates_list[0], zoom_start=17)
    
    for _, coordinate in coordinates_dataset.iterrows():
        folium.Marker(location=[coordinate['latitude'], coordinate['longitude']]).add_to(folium_map)
        
    for _, anomaly in anomalies_dataset.iterrows():
        folium.Marker(location=[anomaly['latitude'], anomaly['longitude']], icon=folium.Icon(color='red'), popup=f"<strong>{anomaly['type']}</strong>").add_to(folium_map)    
    return folium_map._repr_html_()

def on_snapshot_coordinates(doc_snapshot, changes, read_time):
    coordinates_list = []
    for doc in doc_snapshot:
        data = doc.to_dict()
        print(data)
        coordinates_list.append(data)
        coordinates = {
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'timestamp': data.get('timestamp').strftime('%Y-%m-%d %H:%M:%S'),
            'type': data.get('type'),
            'altitude': data.get('altitude'),
            'speed': data.get('speed')
        }
        if coordinates:
            socketio.emit('update_coordinates', {'coordinates': coordinates})
    
    global coordinates_dataset
    coordinates_dataset = pd.concat([coordinates_dataset, data_formatter.create_coordinates_dataset(coordinates_list)], ignore_index=True)
    
def on_snapshot_anomalies(doc_snapshot, changes, read_time):
    anomalies_list = []
    for doc in doc_snapshot:
        data = doc.to_dict()
        print(data)
        anomalies_list.append(data)
        anomaly = {
            'type': data.get('type'),
            'value': data.get('value'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'timestamp': data.get('timestamp').strftime('%Y-%m-%d %H:%M:%S')
        }
        socketio.emit('update_anomalies', {'anomaly': anomaly})
    global anomalies_dataset
    anomalies_dataset = pd.concat([anomalies_dataset, data_formatter.create_anomalies_dataset(anomalies_list)], ignore_index=True)

doc_ref = db.collection('coordinates')
doc_ref.on_snapshot(on_snapshot_coordinates)

doc_ref = db.collection('anomalies')
doc_ref.on_snapshot(on_snapshot_anomalies)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/plot.png')
def plot_png():
    plot.plot(anomalies_dataset)
    # Genera un grafico con Seaborn
    # fig, ax = plt.subplots()
    # sns.set(style="whitegrid")
    # print(anomalies_dataset['timestamp'].head(1))
    # print(coordinates_dataset.head())
    # # Simula alcuni dati
    # data = sns.load_dataset("tips")
    # sns.barplot(x="day", y="total_bill", data=data, ax=ax)

    # # Salva il grafico in un buffer
    # img = io.BytesIO()
    # plt.savefig(img, format='png')
    # img.seek(0)
    # plt.close(fig)
    # return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    socketio.run(app)