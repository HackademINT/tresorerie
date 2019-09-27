#!/usr/bin/python3
from datetime import datetime
from flask import jsonify, request, abort, json
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from models import *


# Initialize authentication

def authenticate(username, password):
    api_user = APIuser.query.filter_by(username=username).first()
    if api_user and safe_str_cmp(api_user.password.encode('utf-8'), password.encode('utf-8')):
        return api_user

def identity(payload):
        api_user_id = payload['identity']
        return APIuser.query.get(api_user_id)

jwt = JWT(app, authenticate, identity)


# Default route

@app.route('/', methods=['GET'])
def default():
    author = 'meroupatate'
    followme = 'https://github.com/meroupatate'
    message = {'author': author, 'followme': followme}
    return jsonify(message)


# User routes

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route('/user', methods=['POST'])
@jwt_required()
def add_user():
    data = json.loads(request.json)
    fname = data['fname']
    lname = data['lname']
    email = data['email']
    new_user = User(fname=fname, lname=lname, email=email)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201

@app.route('/user', methods=['GET'])
@jwt_required()
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

@app.route('/user/<id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404, f'User not found for id: {id}')
    return user_schema.jsonify(user)

@app.route('/user/<id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404, f'User not found for id: {id}')
    data = json.loads(request.json)
    user.fname = data['fname']
    user.lname = data['lname']
    user.email = data['email']
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/user/<id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404, f'User not found for id: {id}')
    try:
        db.session.delete(user)
        db.session.commit()
        return '', 204
    except IntegrityError:
        abort(405, f'User {id} can\'t be deleted since there are transactions depending on this object')


# Event routes

event_schema = EventSchema()
events_schema = EventSchema(many=True)

@app.route('/event', methods=['POST'])
@jwt_required()
def add_event():
    data = json.loads(request.json)
    name = data['name']
    date = datetime.strptime(data['date'], '%Y-%m-%d')
    description = data['description']
    new_event = Event(name=name, date=date, description=description)
    db.session.add(new_event)
    db.session.commit()
    return event_schema.jsonify(new_event), 201

@app.route('/event', methods=['GET'])
@jwt_required()
def get_events():
    all_events = Event.query.all()
    result = events_schema.dump(all_events)
    return jsonify(result)

@app.route('/event/<id>', methods=['GET'])
@jwt_required()
def get_event(id):
    event = Event.query.filter_by(id=id).first()
    if event is None:
        abort(404, f'Event not found for id: {id}')
    return event_schema.jsonify(event)

@app.route('/event/<id>', methods=['PUT'])
@jwt_required()
def update_event(id):
    event = Event.query.filter_by(id=id).first()
    if event is None:
        abort(404, f'Event not found for id: {id}')
    data = json.loads(request.json)
    event.name = data['name']
    event.date = datetime.strptime(data['date'], '%Y-%m-%d')
    event.description = data['description']
    db.session.commit()
    return event_schema.jsonify(event)

@app.route('/event/<id>', methods=['DELETE'])
@jwt_required()
def delete_event(id):
    event = Event.query.filter_by(id=id).first()
    if event is None:
        abort(404, f'Event not found for id: {id}')
    try:
        db.session.delete(event)
        db.session.commit()
        return '', 204
    except IntegrityError:
        abort(405, f'Event {id} can\'t be deleted since there are transactions depending on this object')


# Transaction routes

transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)

@app.route('/transaction', methods=['POST'])
@jwt_required()
def add_transaction():
    data = json.loads(request.json)
    sum = data['sum']
    type = data['type']
    onhold = data['onhold']
    description = data['description']
    user_id = data['user_id']
    event_id = data['event_id']
    new_transaction = Transaction(sum=sum, onhold=onhold, type=type, user_id=user_id, event_id=event_id, description=description)
    db.session.add(new_transaction)
    db.session.commit()
    return transaction_schema.jsonify(new_transaction), 201

@app.route('/transaction', methods=['GET'])
@jwt_required()
def get_transactions():
    all_transactions = Transaction.query.all()
    result = transactions_schema.dump(all_transactions)
    return jsonify(result)

@app.route('/transaction/<id>', methods=['GET'])
@jwt_required()
def get_transaction(id):
    transaction = Transaction.query.get(id)
    if transaction is None:
        abort(404, f'Transaction not found for id: {id}')
    return transaction_schema.jsonify(transaction)

@app.route('/transaction/<id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    transaction = Transaction.query.filter_by(id=id).first()
    if transaction is None:
        abort(404, f'Transaction not found for id: {id}')
    data = json.loads(request.json)
    transaction.sum = data['sum']
    transaction.type = data['type']
    transaction.onhold = data['onhold']
    transaction.description = data['description']
    if data.get('user_id', '') != '':
        transaction.user_id = data['user_id']
    if data.get('event_id', '') != '':
        transaction.event_id = data['event_id']
    db.session.commit()
    return transaction_schema.jsonify(transaction)

@app.route('/transaction/<id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    transaction = Transaction.query.filter_by(id=id).first()
    if transaction is None:
        abort(404, f'Transaction not found for id: {id}')
    try:
        db.session.delete(transaction)
        db.session.commit()
        return '', 204
    except IntegrityError:
        abort(405, f'Event {id} can\'t be deleted since there are transactions depending on this object')


if __name__ == '__main__':
    db.create_all()
    app.run(host='localhost', port=8155, debug=True)
