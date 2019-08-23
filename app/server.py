#!/usr/bin/python3.7

from functools import wraps
from flask import Flask, g, session, render_template, request, redirect, flash, url_for
from flask_simpleldap import LDAP
from queries import *
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
ldap = LDAP(app)

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = {}
        g.ldap_groups = ldap.get_user_groups(user=session['user_id'])

@app.route("/")
@ldap.login_required
def default():
    return render_template('index.html', events=get_events(), 
                          users=get_users(), total=get_total_inflow()-get_total_outflow(), 
                           total_event=count_events(),
                           total_onhold=get_total_onhold(),
                           user=sort_users_by_onhold()[0])


@app.route("/admin", methods=['GET', 'POST'])
@ldap.group_required([b'admin'])
def admin():
    if request.method == 'GET':
        events = sorted(get_events(), key=lambda e: e['id'], reverse=True)
        users = sorted(get_users(), key=lambda u: u['id'], reverse=True)
        return render_template('admin.html', users=users, events=events, transactions=get_transactions())
    else:
        description = request.form['description']
        sum = float(request.form['sum'])
        type = True if request.form['type'] == '1' else False
        onhold = True if request.form['onhold'] == '1' else False
        transaction = { "user_id": request.form['userId'], 
                       "event_id": request.form['eventId'],
                       "sum": request.form['sum'],
                       "description": request.form['description'],
                       "type": type,
                       "onhold": onhold }
        status = add_transaction(transaction)
        if status == 201:
            flash('Transaction ajoutée avec succès', 'succes')
        else:
            flash('Erreur lors de l\'ajout de la transaction', 'error')
        return redirect(url_for('admin'))



@app.route("/pay")
def remboursement():
    return render_template('pay.html')


@app.route("/event/<id>")
def event(id):
    event = get_event_with_username(id)
    return render_template('event.html', event=event)


@app.route("/user/<id>")
def user(id):
    user = get_user_with_eventname(id)
    return render_template('user.html', user=user)


@app.route("/login",methods=["GET","POST"])
def login():
    if g.user:
        return redirect(url_for('default'))
    if request.method == 'POST':
        user = request.form['user']
        passwd = request.form['passwd']
        test = ldap.bind_user(user, passwd)
        if test is None or passwd == '':
            return 'Invalid credentials'
        else:
            session['user_id'] = request.form['user']
            return redirect('/')
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.errorhandler(404)
def error404(error): 
    return redirect(url_for('default'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8154, debug=True)
