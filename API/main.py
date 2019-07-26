#!/usr/bin/python3
from datetime import datetime
from flask import jsonify, request, abort
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
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

user_schema = UserSchema(strict=True)
users_schema = UserSchema(many=True, strict=True)

@app.route('/user', methods=['POST'])
@jwt_required()
def add_user():
    fname = request.json['fname']
    lname = request.json['lname']
    email = request.json['email']
    new_user = User(fname=fname, lname=lname, email=email)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201

@app.route('/user', methods=['GET'])
@jwt_required()
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)

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
    user.fname = request.json['fname']
    user.lname = request.json['lname']
    user.email = request.json['email']
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/user/<id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404, f'User not found for id: {id}')
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user), 204


# Event routes

event_schema = EventSchema(strict=True)
events_schema = EventSchema(many=True, strict=True)

@app.route('/event', methods=['POST'])
@jwt_required()
def add_event():
    name = request.json['name']
    date = datetime.strptime(request.json['date'], '%Y-%m-%d')
    description = request.json['description']
    new_event = Event(name=name, date=date, description=description)
    db.session.add(new_event)
    db.session.commit()
    return event_schema.jsonify(new_event), 201

@app.route('/event', methods=['GET'])
@jwt_required()
def get_events():
    all_events = Event.query.all()
    result = events_schema.dump(all_events)
    return jsonify(result.data)

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
    event.name = request.json['name']
    event.date = datetime.strptime(request.json['date'], '%Y-%m-%d')
    event.description = request.json['description']
    db.session.commit()
    return event_schema.jsonify(event)

@app.route('/event/<id>', methods=['DELETE'])
@jwt_required()
def delete_event(id):
    event = Event.query.filter_by(id=id).first()
    if event is None:
        abort(404, f'Event not found for id: {id}')
    db.session.delete(event)
    db.session.commit()
    return '', 204


# Transaction routes

transaction_schema = TransactionSchema(strict=True)
transactions_schema = TransactionSchema(many=True, strict=True)

@app.route('/transaction', methods=['POST'])
@jwt_required()
def add_transaction():
    sum = request.json['sum']
    type = request.json['type']
    onhold = request.json['onhold']
    description = request.json['description']
    user_id = request.json['user_id']
    event_id = request.json['event_id']
    new_transaction = Transaction(sum=sum, onhold=onhold, type=type, user_id=user_id, event_id=event_id, description=description)
    db.session.add(new_transaction)
    db.session.commit()
    return transaction_schema.jsonify(new_transaction), 201

@app.route('/transaction', methods=['GET'])
@jwt_required()
def get_transactions():
    all_transactions = Transaction.query.all()
    result = transactions_schema.dump(all_transactions)
    return jsonify(result.data)

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
    transaction.sum = request.json['sum']
    transaction.type = request.json['type']
    transaction.onhold = request.json['onhold']
    transaction.description = request.json['description']
    transaction.user_id = request.json['user']
    transaction.event_id = request.json['event']
    db.session.commit()
    return transaction_schema.jsonify(transaction)

@app.route('/transaction/<id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    transaction = Transaction.query.filter_by(id=id).first()
    if transaction is None:
        abort(404, f'Transaction not found for id: {id}')
    db.session.delete(transaction)
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=8155, debug=True)
