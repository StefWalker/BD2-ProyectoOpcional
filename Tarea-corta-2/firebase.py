import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

if __name__ == '__main__':
    # Fetch the service account key JSON file contents
    cred = credentials.Certificate('adminSecret.json')

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://tareacorta2-2f12e-default-rtdb.firebaseio.com/'
    })
    ref = db.reference('/')
    ref.set({
        'Community':{
            'person':{
                'friends': ['leemxch@gmail.com', 'leemxch', 'another']
            }
        },
        'Navigate':{
            'mark':{
                'latitude': 123,
                'longitude': 1
            }
        }
    })