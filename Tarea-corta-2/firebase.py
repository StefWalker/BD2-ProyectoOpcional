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
        'Users':{
            'id': 'uid',
            'email': 'fake@gmail.com',
            'friends': ['init']
        },
        'Community':{
            'name': 'Public',
            'participantes': ['init'],
            'messages': ['init']
        },
        'Markers': {
           'id': 1,
            'latitud': 0,
            'longitud': 0,
            'peligro': 1,
            'fecha': '30/10/2022',
           'hora': '12:00',
            'mensaje': 'Mensaje escrito by user',
            'ubicacion': 1,
            'votos': 1,
            'ultimaModificacion': '30/10/2022'
        }
    })
    print(ref.get())