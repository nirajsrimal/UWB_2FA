import hashlib
import json
import random
import uuid

import firebase_admin
import time

from flask import Flask, request, jsonify
from flask_sockets import Sockets
from firebase_admin import credentials, firestore

# Initialize firebase
cred = credentials.Certificate("./firebase-key.json")
fb_app = firebase_admin.initialize_app(cred)
fs_client = firestore.client(fb_app)

user_collection = fs_client.collection('users')
attempt_collection = fs_client.collection('attempts')

# Initialize flask
app = Flask(__name__)
sockets = Sockets(app)

available_patterns = ['rectangle', 'triangle', 'pentagon', 'circle']


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@sockets.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        print(message)
        ws.send(message)


@app.route('/signup', methods=['POST'])
def signup():
    req_body = json.loads(request.data)

    matches = user_collection.where('username', '==', req_body['username']).get()
    if len(matches) != 0:
        return "User exists", 400

    user_collection.add({
        'username': req_body['username'],
        'password': hashlib.sha256(req_body['password'].encode('utf-8')).hexdigest(),
        'name': req_body['name'],
        'tag_id': req_body['tag_id']
    })

    return jsonify({
        'success': True
    })


@app.route('/login', methods=['POST'])
def login():
    req_body = json.loads(request.data)

    matches = user_collection.where('username', '==', req_body['username']).get()
    if len(matches) == 0:
        return jsonify({
            'success': False,
            'message': 'Invalid User!'
        }), 401

    print(matches[0].get('password'))
    if matches[0].get('password') != hashlib.sha256(req_body['password'].encode('utf-8')).hexdigest():
        return jsonify({
            'success': False,
            'message': 'Invalid Password!'
        }), 401

    attempts = attempt_collection\
        .where('username', '==', req_body['username'])\
        .order_by('started_at', 'DESCENDING')\
        .get()

    if len(attempts) > 0 and int(attempts[0].get('started_at')) > int(time.time() - 60):
        return jsonify({
            'success': False,
            'message': 'Someone just tried to login. Please try again after a minute.'
        }), 401

    chosen_pattern = random.choice(available_patterns)
    assigned_token = uuid.uuid4()
    attempt_collection.add({
        "username": req_body['username'],
        "pattern": chosen_pattern,
        "started_at": int(time.time() - 60),
        "tag_id": matches[0]["tag_id"],
        "token": assigned_token
    })

    return jsonify({
        'success': True,
        'message': 'Successfully identified user, verify tag',
        'tag_id': matches[0]['tag_id'],
        'name': matches[0]['name'],
        'token': assigned_token
    })


if __name__ == '__main__':
    app.run(debug=True)
