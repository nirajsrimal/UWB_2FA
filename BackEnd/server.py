import hashlib
import json
import os
import random
import uuid
import firebase_admin
import time

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from firebase_admin import credentials, firestore

from solver import get_shape

# Initialize firebase
cred = credentials.Certificate("./firebase-key.json")
fb_app = firebase_admin.initialize_app(cred)
fs_client = firestore.client(fb_app)

user_collection = fs_client.collection('users')
attempt_collection = fs_client.collection('attempts')

# Initialize flask
app = Flask(__name__)
socket_io = SocketIO(app, cors_allowed_origins="*")

mode = os.environ.get('MODE', 'OPENCV')
print("Starting server with {} backend".format(mode))

if mode == 'OPENCV':
    available_patterns = ['rectangle', 'triangle', 'pentagon', 'hexagon', 'circle']
else:
    # available_patterns = ['square', 'triangle', 'circle']
    available_patterns = ['circle']


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


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
    assigned_token = str(uuid.uuid4())
    attempt_collection.add({
        "username": req_body['username'],
        "pattern": chosen_pattern,
        "started_at": int(time.time() - 60),
        "tag_id": matches[0].get("tag_id"),
        "token": assigned_token
    })

    return jsonify({
        'success': True,
        'message': 'Successfully identified user, verify tag',
        'tag_id': matches[0].get('tag_id'),
        'name': matches[0].get('name'),
        'token': assigned_token
    })


state = {
    'inputs': [],
    'pattern': None
}


@socket_io.on('token')
def handle_token(token):
    attempts = attempt_collection.where('token', '==', token).get()
    if len(attempts) > 0:
        state['pattern'] = attempts[0].get('pattern')
        print("Expecting shape: " + str(state.get('pattern')))
        emit('token_ack', state['pattern'])
    else:
        emit('token_na')


@socket_io.on("data")
def handle_data(data):
    state['inputs'].append((data["ev_num"], data['x'], data['y']))
    # print(state['inputs'])


@socket_io.on("retry")
def handle_retry():
    print("Retry requested, clearing state")
    state['inputs'] = []


@socket_io.on("disconnect")
def handle_disc():
    print("Connection closed, clearing state")
    state['inputs'] = []
    state['pattern'] = None


@socket_io.on("finalize")
def compute_result():
    print("Computing result")
    computed_shape = get_shape(state['inputs'], use_ml=(mode != 'OPENCV'))
    if computed_shape == state['pattern']:
        print("Successful pattern!")
        emit("computed_result", {'success': 'true', 'token': "success"})
    else:
        print("Expected {}, got {}".format(state['pattern'], computed_shape))
        emit("computed_result", {'success': 'false'})

    state['inputs'] = []
    state['pattern'] = None


if __name__ == '__main__':
    socket_io.run(app)
