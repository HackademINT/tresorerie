#!/usr/bin/python3.7

from functools import wraps
from flask import Flask, g, session, render_template, request, redirect, flash, url_for
from flask_caching import Cache
from flask_simpleldap import LDAP
from datetime import datetime
from queries import *
from config import Config


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
                           user=get_worst_user())


@app.route("/admin", methods=['GET', 'POST'])
@ldap.group_required([b'admin'])
def admin():
    if request.method == 'GET':
        events = sorted(get_events(), key=lambda e: e['id'], reverse=True)
        users = sorted(get_users(), key=lambda u: u['id'], reverse=True)
        return render_template('admin.html', users=users, events=events, transactions=get_transactions())
    else:
        action = request.form['action']
        if action == 'delete':
            status = delete_transaction(request.form['tid'])
            if status == 204:
                flash('Transaction supprimée avec succès', 'success')
            else:
                flash('Erreur lors de la suppression de la transaction', 'error')
        else:
            type = True if request.form['type'] == '1' else False
            onhold = True if request.form['onhold'] == '1' else False
            transaction = {
                    "sum": request.form['sum'],
                    "description": request.form['description'],
                    "type": type,
                    "onhold": onhold
                    }
            if action == 'add':
                transaction.update({"user_id": request.form["userId"], "event_id": request.form["eventId"]})
                status = add_transaction(transaction)
                if status == 201:
                    flash('Transaction ajoutée avec succès', 'success')
                else:
                    flash('Erreur lors de l\'ajout de la transaction', 'error')
            elif action == 'modify':
                transaction.update({"tid": request.form['tid']})
                status = modify_transaction(transaction)
                if status == 200:
                    flash('Transaction modifiée avec succès', 'success')
                else:
                    flash('Erreur lors de la modification de la transaction', 'error')
    return redirect(url_for('admin'))


@app.route("/admin/events", methods=['GET', 'POST'])
@ldap.group_required([b'admin'])
def admin_events():
    if request.method == 'GET':
        events = sorted(get_events(), key=lambda e: e['id'], reverse=True)
        return render_template('admin-events.html', events=events)
    else:
        action = request.form['action']
        if action == 'delete':
            status = delete_event(request.form['eid'])
            if status == 204:
                flash('Evènement supprimé avec succès', 'success')
            else:
                flash('Erreur lors de la suppression de l\'évènement', 'error')
        else:
            date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            event = {"name": request.form['name'],
                    "date": date.strftime('%Y-%m-%d'),
                    "description": request.form['description']}
            if action == 'add':
                status = add_event(event)
                if status == 201:
                    flash('Evènement ajouté avec succès', 'success')
                else:
                    flash('Erreur lors de l\'ajout de l\'évènement', 'error')
            elif action == 'modify':
                event.update({"eid": request.form['eid']})
                status = modify_event(event)
                if status == 200:
                    flash('Evènement modifié avec succès', 'success')
                else:
                    flash('Erreur lors de la modification de l\'évènement', 'error')
    return redirect(f'/admin/events')


@app.route("/admin/users", methods=['GET', 'POST'])
@ldap.group_required([b'admin'])
def admin_users():
    if request.method == 'GET':
        users = sorted(get_users(), key=lambda e: e['id'], reverse=True)
        return render_template('admin-users.html', users=users)
    else:
        action = request.form['action']
        if action == 'delete':
            status = delete_user(request.form['uid'])
            if status == 204:
                flash('Utilisateur supprimé avec succès', 'success')
            else:
                flash('Erreur lors de la suppression de l\'utilisateur', 'error')
        else:
            user = {"fname": request.form['fname'],
                    "lname": request.form['lname'],
                    "email": request.form['email']}
            if action == 'add':
                status = add_user(user)
                if status == 201:
                    flash('Utilisateur ajouté avec succès', 'success')
                else:
                    flash('Erreur lors de l\'ajout de l\'utilisateur', 'error')
            elif action == 'modify':
                user.update({"uid": request.form['uid']})
                status = modify_user(user)
                if status == 200:
                    flash('Utilisateur modifié avec succès', 'success')
                else:
                    flash('Erreur lors de la modification de l\'utilisateur', 'error')
    return redirect(f'/admin/users')


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
def login():
    if g.user:
        return redirect(url_for('default'))
    if request.method == 'POST':
        user = request.form['user']
        passwd = request.form['passwd']
        test = ldap.bind_user(user, passwd)
        if test is None or passwd == '':
            flash('Echec d\'authentification', 'error')
            return redirect(url_for('login'))
        else:
            user = request.form['user']
            session['user_id'] = user
            flash(f'Bienvenue {user}', 'success')
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
