import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore import GeoPoint

cred = credentials.Certificate('service_account_key.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def store_coordinate(data):
    doc_ref = db.collection('coordinates').document()
    doc_ref.set({
        'latitude': data[1],
        'longitude': data[2],
        'altitude': data[3],
        'speed': data[4],
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    
def store_anomalie(data):
    print(data)
    doc_ref = db.collection('anomalies').document()
    doc_ref.set({
        'type': data[0],
        'value': data[1],
        'latitude': data[2],
        'longitude': data[3],
        'timestamp': firestore.SERVER_TIMESTAMP
    })