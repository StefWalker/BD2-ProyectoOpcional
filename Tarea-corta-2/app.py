import firebase_admin
import json
from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, jsonify, request
from flask_ngrok import run_with_ngrok
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
run_with_ngrok(app)

cred = credentials.Certificate('adminSecret.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tareacorta2-2f12e-default-rtdb.firebaseio.com/'
})

####
# Main get request for all elements in the json from firebase
# 

@app.route('/', methods=["GET"])
def getData():
    ref = db.reference('/')
    return jsonify(ref.get())

@app.route('/users', methods=["GET"])
def getUsers():
    ref = db.reference('/Users')
    return jsonify(ref.get())

@app.route('/community', methods=["GET"])
def geCommunity():
    ref = db.reference('/Community')
    return jsonify(ref.get())

####
# Users request
# 

# Add user to the database
@app.route('/user', methods=['POST'])
def addUser():
    # Global JSON path
    ref = db.reference('/')
    # Create a child in the node Users
    ref.child("Users").child(str(request.json['id'])).set({
        'email': request.json['email'],
        'friends': request.json['friends']
    })
    return jsonify(ref.get())

# Add friend from a user UID
@app.route('/addFriend/<int:data>', methods=['POST'])
def addFriend(data):
    # Global JSON path
    ref = db.reference('/Users/' + str(data))
    # Get all the data from the reference
    user = ref.get()
    try:
        # Update the friends list
        ref.update({
            'friends': user["friends"] + [request.json['id']]
        })
    except:
        # Create a list of friends if they dont have one
        ref.update({
            'friends': [request.json['id']]
        })
    return jsonify(ref.get())

####
# Community request
#

# Add group of community to the database
@app.route('/addGroup/<int:data>', methods=['POST'])
def addGroup(data):
    # Global JSON path
    ref = db.reference('/')
    # Create a child in the node Community
    ref.child("Community").child(str(request.json['name'])).set({
        'participants': [data],
        'messages': ["Welcome to " + request.json['name'] + "'s group"]
    })
    return jsonify(ref.get())

# Add a message to the group to the database
@app.route('/addMessageGroup/<name>', methods=['POST'])
def addMessageGroup(name):
    # Path for the community node with the specific group
    ref = db.reference('/Community/' + str(name))
    # Get all the data from the reference
    group = ref.get()
    ref.update({
        # Add message to the list
        'messages': group["messages"] + [request.json['message']]
    })
    return jsonify(ref.get())

# Add participant to a group
@app.route('/addPerson/<name>', methods=['POST'])
def addPerson(name):
    ref = db.reference('/Community/' + str(name))
    # Get all the data from the reference
    group = ref.get()
    try:
        # Update the participants list
        ref.update({
            'participants': group["participants"] + [request.json['id']]
        })
    except:
        # Create the participants list if they dont have one
        ref.update({
            'participants': [request.json['id']]
        })
    return jsonify(ref.get())

####
# Markers request
#

# Add a marker to the database
@app.route('/marker', methods=['POST'])
def addMarker():
    # Global JSON path
    ref = db.reference('/')
    ref.child("Markers").child(str(request.json['title'])).set({
        'latitude': request.json['latitude'],
        'longitude': request.json['longitude'],
        'danger': request.json['danger'],
        'date': request.json['date'],
        'hour': request.json['hour'],
        'message': request.json['message'],
        'comments': [request.json['comment']],
        'ubication': request.json['ubication'],
        'vote': 1,
        'lastModification': request.json['lastMod']
    })
    return jsonify(ref.get())

# Add a comment to the comments
@app.route('/comment/<name>', methods=['POST'])
def addComment(name):
    # Path to the Marker node with the specific marker
    ref = db.reference('/Markers/' + str(name))
    # Get all the data from the reference
    marker = ref.get()
    # Add a comment to the comments
    ref.update({
        'comments': marker["comments"] + [request.json['comment']],
        'lastModification': request.json['lastMod']
    })
    return jsonify(ref.get())

# +1 vote
@app.route('/vote/<name>', methods=['POST'])
def vote(name):
    # Path to the Markers node with the specific mark
    ref = db.reference('/Markers/' + str(name))
    # Get all the data from the reference
    group = ref.get()
    # Update +1 to the votes counter
    ref.update({
        'vote': group["vote"] + 1,
        'lastModification': request.json['lastMod']
    })
    return jsonify(ref.get())

# Change danger level
@app.route('/changeDanger/<name>', methods=['POST'])
def changeDanger(name):
    # Path to the Marker node with the specific marker
    ref = db.reference('/Markers/' + str(name))
    # Update the danger level
    ref.update({
        'danger': request.json['danger'],
        'lastModification': request.json['lastMod']
    })
    return jsonify(ref.get())

if __name__ == '__main__':
    app.run()