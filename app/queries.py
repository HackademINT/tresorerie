#!/usr/bin/python3
import requests
import json

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
    return {'total': total, 'inflow': inflow, 'outflow': outflow, 'onhold': onhold, 'onhold_inflow': onhold_inflow, 'onhold_outflow': onhold_outflow}


# User functions

def get_users():
    users = json.loads(s.get(f'{API_URL}/user').text)
    for user in users:
        user.update(get_stats(user['transaction']))
    return users

def get_user(id):
    user = json.loads(s.get(f'{API_URL}/user/{id}').text)
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


# Event functions

def get_events():
    events = json.loads(s.get(f'{API_URL}/event').text)
    for event in events:
        event.update(get_stats(event['transaction']))
    return events

def get_event(id):
    event = json.loads(s.get(f'{API_URL}/event/{id}').text)
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
    events = json.loads(s.get(f'{API_URL}/event').text)
    return len(events)


# Transaction functions

def get_transactions():
    return json.loads(s.get(f'{API_URL}/transaction').text)

def get_transaction(id):
    return json.loads(s.get(f'{API_URL}/transaction/{id}').text)

# Misc stat functions

def get_total_inflow():
    transactions = json.loads(s.get(f'{API_URL}/transaction').text)
    return sum([transaction['sum'] for transaction in transactions if transaction['type'] and not transaction['onhold']])

def get_total_outflow():
    transactions = json.loads(s.get(f'{API_URL}/transaction').text)
    return sum([transaction['sum'] for transaction in transactions if not transaction['type'] and not transaction['onhold']])

def get_total_onhold():
    transactions = json.loads(s.get(f'{API_URL}/transaction').text)
    return sum([transaction['sum'] for transaction in transactions if transaction['onhold'] and transaction['type']])\
            - sum([transaction['sum'] for transaction in transactions if transaction['onhold'] and not transaction['type']])

def sort_users_by_onhold():
    return sorted(get_users(), key=lambda user: user['onhold'], reverse=True)
