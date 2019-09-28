#!/usr/bin/python3
import requests
import json
from config import headers


API_URL = 'http://127.0.0.1:8155'

s = requests.session()


# Get json containing total, paid and unpaid for a list of transaction

def get_stats(transactions):
    inflow = sum(transaction['sum'] for transaction in transactions if transaction['type'] and not transaction['onhold'])
    outflow = sum(transaction['sum'] for transaction in transactions if not transaction['type'] and not transaction['onhold'])
    total = inflow - outflow
    onhold_inflow = sum(transaction['sum'] for transaction in transactions if transaction['onhold'] and transaction['type'])
    onhold_outflow = sum(transaction['sum'] for transaction in transactions if transaction['onhold'] and not transaction['type'])
    onhold = onhold_inflow - onhold_outflow
    return {'total': total, 'total_preview': total + onhold, 'inflow': inflow, 'outflow': outflow, 'onhold': onhold, 'onhold_inflow': onhold_inflow, 'onhold_outflow': onhold_outflow}


# User functions

def get_users():
    users = json.loads(s.get(f'{API_URL}/user', headers=headers).text)
    for user in users:
        user.update(get_stats(user['transaction']))
    return users

def get_user(id):
    user = json.loads(s.get(f'{API_URL}/user/{id}', headers=headers).text)
    user.update(get_stats(user['transaction']))
    return user

def get_user_with_eventname(id):
    user = get_user(id)
    events = {}
    for event in get_events():
        events.update({event['id']: event["name"]})
    for transaction in user['transaction']:
        transaction.update({'eventname': events[transaction['event']]})
    return user

def add_user(user):
    add = s.post(f'{API_URL}/user', json=json.dumps(user), headers=headers)
    return add.status_code

def delete_user(uid):
    delete = s.delete(f'{API_URL}/user/{uid}', headers=headers)
    return delete.status_code

def modify_user(user):
    modify = s.put(f'{API_URL}/user/{user["uid"]}', json=json.dumps(user), headers=headers)
    return modify.status_code

# Event functions

def get_events():
    events = json.loads(s.get(f'{API_URL}/event', headers=headers).text)
    for event in events:
        event.update(get_stats(event['transaction']))
    return events

def get_event(id):
    event = json.loads(s.get(f'{API_URL}/event/{id}', headers=headers).text)
    event.update(get_stats(event['transaction']))
    return event

def get_event_with_username(id):
    event = get_event(id)
    users = {}
    for user in get_users():
        users.update({user['id']: f'{user["fname"]} {user["lname"]}'})
    for transaction in event['transaction']:
        transaction.update({'username': users[transaction['user']]})
    return event

def count_events():
    events = json.loads(s.get(f'{API_URL}/event', headers=headers).text)
    return len(events)

def add_event(event):
    add = s.post(f'{API_URL}/event', json=json.dumps(event), headers=headers)
    return add.status_code

def delete_event(eid):
    delete = s.delete(f'{API_URL}/event/{eid}', headers=headers)
    return delete.status_code

def modify_event(event):
    modify = s.put(f'{API_URL}/event/{event["eid"]}', json=json.dumps(event), headers=headers)
    return modify.status_code


# Transaction functions

def get_transactions():
    return json.loads(s.get(f'{API_URL}/transaction', headers=headers).text)

def get_transaction(id):
    return json.loads(s.get(f'{API_URL}/transaction/{id}', headers=headers).text)

def add_transaction(transaction):
    add = s.post(f'{API_URL}/transaction', json=json.dumps(transaction), headers=headers)
    return add.status_code

def delete_transaction(tid):
    delete = s.delete(f'{API_URL}/transaction/{tid}', headers=headers)
    return delete.status_code

def modify_transaction(transaction):
    modify = s.put(f'{API_URL}/transaction/{transaction["tid"]}', json=json.dumps(transaction), headers=headers)
    return modify.status_code


# Misc stat functions

def sort_users_by_onhold():
    return sorted(get_users(), key=lambda user: user['onhold'], reverse=True)

def get_worst_user():
    users = [user for user in sort_users_by_onhold() if user['onhold'] > 0]
    if len(users) == 0:
        return None
    return users[0]

def sort_users_by_total():
    return sorted(get_users(), key=lambda user: user['total'], reverse=True)

def get_best_user():
    users = [user for user in sort_users_by_total() if user['total'] > 0]
    if len(users) == 0:
        return None
    return users[0]
