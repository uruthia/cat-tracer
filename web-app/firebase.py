import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore import GeoPoint

cred = credentials.Certificate('service_account_key.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def get_coordinates():
    docs = db.collection('coordinates').get()
    coordinates = []
    for doc in docs:
        coordinates.append(doc.to_dict())
    return coordinates

def get_anomalies():
    docs = db.collection('anomalies').get()
    anomalies = []
    for doc in docs:
        anomalies.append(doc.to_dict())
    return anomalies