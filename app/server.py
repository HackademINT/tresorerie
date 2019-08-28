#!/usr/bin/python3.7

from functools import wraps
from flask import Flask, g, session, render_template, request, redirect, flash, url_for
from flask_simpleldap import LDAP
from flask_caching import Cache
from queries import *
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
ldap = LDAP(app)

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = {}
        g.ldap_groups = ldap.get_user_groups(user=session['user_id'])

@app.route("/")
@cache.cached(timeout=60)
@ldap.login_required
def default():
    return render_template('index.html', events=get_events(),
                          users=get_users(), total=get_total_inflow()-get_total_outflow(),
                           total_event=count_events(),
                           total_onhold=get_total_onhold(),
                           user=sort_users_by_onhold()[0])


@app.route("/admin", methods=['GET', 'POST'])
@cache.cached(timeout=60)
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


@app.route("/admin/<tab>", methods=['GET', 'POST'])
@cache.cached(timeout=60)
@ldap.group_required([b'admin'])
def admin_tabs(tab):
    if tab not in ['users', 'events']:
        return redirect(url_for('admin'))
    else:
        if request.method == 'GET':
            if tab == 'events':
                events = sorted(get_events(), key=lambda e: e['id'], reverse=True)
                return render_template('admin-events.html', events=events)
            else:
                users = sorted(get_users(), key=lambda e: e['id'], reverse=True)
                return render_template('admin-users.html', users=users)
        else:
            if tab == 'events':
                description = request.form['description']
                name = request.form['name']
                date = request.form['date']
                date = datetime.strptime(request.form['date'], '%Y-%m-%d')
                event = {"name": name,
                        "date": date.strftime('%Y-%m-%d'),
                        "description": description}
                status = add_event(event)
                if status == 201:
                    flash('Evènement ajouté avec succès', 'success')
                else:
                    flash('Erreur lors de l\'ajout de l\'évènement', 'error')
            else:
                fname = request.form['fname']
                lname = request.form['lname']
                email = request.form['email']
                user = {"fname": fname,
                        "lname": lname,
                        "email": email}
                status = add_user(user)
                if status == 201:
                    flash('Utilisateur ajouté avec succès', 'success')
                else:
                    flash('Erreur lors de l\'ajout de l\'utilisateur', 'error')
            return redirect(f'/admin/{tab}')


@app.route("/pay")
@cache.cached(timeout=3600)
def remboursement():
    return render_template('pay.html')


@app.route("/event/<id>")
@cache.cached(timeout=60)
def event(id):
    event = get_event_with_username(id)
    return render_template('event.html', event=event)


@app.route("/user/<id>")
@cache.cached(timeout=60)
def user(id):
    user = get_user_with_eventname(id)
    return render_template('user.html', user=user)


@app.route("/login",methods=["GET","POST"])
@cache.cached(timeout=3600)
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
    app.run(host='localhost', port=8154, debug=True)
