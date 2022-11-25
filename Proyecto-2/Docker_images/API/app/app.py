import time
import os
import sys
import pika
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, jsonify, request
from flask_ngrok import run_with_ngrok
from flask_cors import CORS
from flask import Flask, jsonify, request
from flask_ngrok import run_with_ngrok
from flask_cors import CORS

app = Flask(__name__)
#run_with_ngrok(app)
CORS(app)

cred = credentials.Certificate('adminSecret.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tareacorta2-2f12e-default-rtdb.firebaseio.com/'
})

@app.route('/', methods=["GET"])
def default():
    apiPage = 0
    count = 0
    articles= []
    while count < 100:
        response = requests.get("https://api.biorxiv.org/covid19/" + str(apiPage)).json()
        count += response["messages"][0]["count"]
        apiPage += 1
        articles += response["collection"]
    response["collection"] = articles
    return response


@app.route('/likes/<int:data>', methods=["GET"])
def getLikes(data):
    # Global JSON path
    ref = db.reference('/Users/' + str(data) + '/articles')
    # Get all the data from the reference
    user = ref.get()
    return jsonify(ref.get())

# Add user to the database
@app.route('/user', methods=['POST'])
def addUser():
    # Global JSON path
    ref = db.reference('/')
    # Create a child in the node Users
    ref.child("Users").child(str(request.json['id'])).set({
        'email': request.json['email']
    })
    return jsonify(ref.get())

@app.route('/addLike/<int:data>', methods=["POST"])
def addLike(data):
    # Global JSON path
    ref = db.reference('/Users/' + str(data))
    # Get all the data from the reference
    user = ref.get()
    try:
        # Update the articles list
        ref.update({
            'articles': user["articles"] + [[request.json['id'],request.json['id']]]
        })
    except:
        # Create a list of articles if they dont have one
        ref.update({
            'articles': [[request.json['id'],request.json['id']]]
        })
    return jsonify(ref.get())

app.run()