import time
import datetime
import os
import sys
import pika
import re
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

@app.route('/search', methods=["POST"])
def default():
    apiPage = 0
    count = 0
    articles= []
    search = request.json["data"]
    while count < 1:
        response = requests.get("https://api.biorxiv.org/covid19/" + str(apiPage)).json()
        if apiPage == response["messages"][0]["total"]:
            break
        if re.search(search.lower(), response["collection"][0]["rel_title"].lower()) != None:
            articles += [response["collection"][0]]
            count += 1
        apiPage += 1
    response["collection"] = articles
    print(len(articles))
    response["messages"][0]["total"] = apiPage + 1
    return response

@app.route('/addLike/<data>', methods=["POST"])
def addLike(data):
    # Global JSON path
    ref = db.reference('/Users/' + str(data))
    # Get all the data from the reference
    user = ref.get()
    try:
        # Update the articles list
        ref.update({
            'articles': user["articles"] + [{"title": request.json['title'], "auth":request.json['auth'], "abs":request.json['abs']}]
        })
    except:
        # Create a list of articles if they dont have one
        ref.update({
            'articles': [{"title": request.json['title'], "auth":request.json['auth'], "abs":request.json['abs']}]
        })
    return jsonify(ref.get())

@app.route('/addGrp/<data>', methods=["POST"])
def addGrp(data):
    print(data)
    return jsonify(data)

app.run()