from datetime import datetime
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials, firestore
import folium
import data_formatter
import pandas as pd
from flask import request

app = Flask(__name__)
socketio = SocketIO(app)

cred = credentials.Certificate('service_account_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
coordinates_dataset = pd.DataFrame()
anomalies_dataset = pd.DataFrame()

def on_snapshot_coordinates(doc_snapshot, changes, read_time):
    coordinates_list = []
    for change in changes:
        if change.type.name == 'ADDED':
            data = change.document.to_dict()
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
    for change in changes:
        if change.type.name == 'ADDED':
            data = change.document.to_dict()
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        date = request.form['date']
        anomalies_df = pd.DataFrame()
        coordinates_df = pd.DataFrame()
        
        anomalies_docs = db.collection('anomalies').get()
        coordinates_docs = db.collection('coordinates').get()
        anomalies = []
        coordinates = []

        for doc in anomalies_docs:
            anomalies.append(doc.to_dict())
        
        for doc in coordinates_docs:
            coordinates.append(doc.to_dict()) 
            
        anomalies_df = pd.concat([anomalies_df, data_formatter.create_anomalies_dataset(anomalies)], ignore_index=True)
        coordinates_df = pd.concat([coordinates_df, data_formatter.create_coordinates_dataset(coordinates)], ignore_index=True)
        anomalies_df['day'] = anomalies_df['timestamp'].dt.date
        anomalies_df['time'] = anomalies_df['timestamp'].dt.time
        
        coordinates_df['day'] = coordinates_df['timestamp'].dt.date
        coordinates_df['time'] = coordinates_df['timestamp'].dt.time

        if date is None:
            date = anomalies_df['day'].iloc[0]
        else:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        
        anomalies_of_the_day = anomalies_df[anomalies_df['day'] == date]
        coordinates_of_the_day = coordinates_df[coordinates_df['day'] == date]

        anomalies_of_the_day['hour'] = anomalies_of_the_day['timestamp'].dt.hour
        barplot_df = anomalies_of_the_day.groupby(['hour', 'type']).size().reset_index(name='count')
    
        pivot_df = barplot_df.pivot(index='hour', columns='type', values='count')

        pivot_df = pivot_df.reset_index()
        if 'heart_rate' not in pivot_df.columns:
            pivot_df['heart_rate'] = 0
        if 'sound' not in pivot_df.columns:
            pivot_df['sound'] = 0
        pivot_df = pivot_df.fillna(0)
       
        pivot = {
            "labels": pivot_df['hour'].tolist(),
            "sound": pivot_df['sound'].tolist(),
            "heart_rate": pivot_df['heart_rate'].tolist()
        }
        coordinates_of_the_day['time'] = coordinates_of_the_day['time'].apply(lambda x: x.strftime('%H:%M:%S'))
        
        coordinates_of_the_day.sort_values(by='timestamp', inplace=True)
        speed = {
            "labels":coordinates_of_the_day['time'].tolist(),
            "values":coordinates_of_the_day['speed'].tolist()
        }
       
        altitude = {
            "labels": coordinates_of_the_day['time'].tolist(),
            "values": coordinates_of_the_day['altitude'].tolist()
        }
        
        coordinates_of_the_day['speed'] = coordinates_of_the_day['speed'].astype(float)
        coordinates_of_the_day['altitude'] = coordinates_of_the_day['altitude'].astype(float)
        avg_speed = round(coordinates_of_the_day['speed'].mean(), 2)
        avg_altitude = round(coordinates_of_the_day['altitude'].mean(), 2)
        max_speed = round(coordinates_of_the_day['speed'].max(), 2)
        max_altitude = round(coordinates_of_the_day['altitude'].max(), 2)
        
        
        return render_template('dashboard.html', barplot_data={"labels": pivot['labels'], "sound": pivot['sound'], "heart_rate": pivot['heart_rate']}, coordinates_data={ 'speed': speed, 'altitude': altitude }, date=date, max_speed=max_speed, max_altitude=max_altitude, avg_speed=avg_speed, avg_altitude=avg_altitude)
    else:
        return render_template('dashboard.html')
    
@app.route('/map')
def map_view():
    coordinates_df = pd.DataFrame()
    anomalies_df = pd.DataFrame()
    
    anomalies_docs = db.collection('anomalies').get()
    coordinates_docs = db.collection('coordinates').get()
    
    anomalies = []
    coordinates = []
    
    for doc in anomalies_docs:
        anomalies.append(doc.to_dict())
        
    for doc in coordinates_docs:
        coordinates.append(doc.to_dict())
    
    coordinates_df = pd.concat([coordinates_df, data_formatter.create_coordinates_dataset(coordinates)], ignore_index=True)
    anomalies_df = pd.concat([anomalies_df, data_formatter.create_anomalies_dataset(anomalies)], ignore_index=True)

    
    anomalies_df['day'] = anomalies_df['timestamp'].dt.date
    anomalies_df['time'] = anomalies_df['timestamp'].dt.time
    
    coordinates_df['day'] = coordinates_df['timestamp'].dt.date
    coordinates_df['time'] = coordinates_df['timestamp'].dt.time
    
    coordinates_list = [[46.100, 13.262]]  # Coordinate di default
    date = request.args.get('date')
    if date is None or date == '':
        date = coordinates_df['day'].iloc[0]
    else:
        date = datetime.strptime(date, '%Y-%m-%d').date()

    folium_map = folium.Map(location=coordinates_list[0], zoom_start=17)
    
    
    coordinate_of_the_day = coordinates_df[coordinates_df['day'] == date]
    anomalies_of_the_day = anomalies_df[anomalies_df['day'] == date]
    for _, coordinate in coordinate_of_the_day.iterrows():
        print(coordinate)
        try:
            latitude = float(coordinate['latitude'])
            longitude = float(coordinate['longitude'])
          
            folium.Marker(
                location=[latitude, longitude],
                icon=folium.CustomIcon(
                    "./static/marker/pathMarker.png",
                    icon_size=(20, 20)
                    ),
            ).add_to(folium_map)
        except ValueError:
            print(f"Invalid coordinates: {coordinate['latitude']}, {coordinate['longitude']}")
            continue 
        
               
    for _, anomaly in anomalies_of_the_day.iterrows():
        print(anomaly)
        try:
            latitude = float(anomaly['latitude'])
            longitude = float(anomaly['longitude'])
           
            
            folium.Marker(
                location=[latitude, longitude],
                icon=folium.CustomIcon(
                    "./static/marker/soundMarker.png" if anomaly['type'] == 'sound' else "./static/marker/HeartbeatMarker.png",
                    icon_size=(45, 50)
                    ),
            ).add_to(folium_map)
        except ValueError:
            print(f"Invalid coordinates: {anomaly['latitude']}, {anomaly['longitude']}")
            continue 
    return folium_map._repr_html_()

if __name__ == '__main__':
    socketio.run(app)