import time
import os
import sys
import pika
import requests
from flask import Flask, jsonify, request
from flask_ngrok import run_with_ngrok
from flask_cors import CORS

app = Flask(__name__)
run_with_ngrok(app)
CORS(app)

@app.route('/', methods=["GET"])
def default():
    apiPage = 0
    count = 0
    articles= []
    while count < 100:
        response = requests.get("https://api.biorxiv.org/covid19/" + str(apiPage)).json()
        if response[]
        count += response["messages"][0]["count"]
        apiPage += 1
        articles += response["collection"]
    response["collection"] = articles
    return response

app.run()