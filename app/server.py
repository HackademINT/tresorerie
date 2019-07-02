#!/usr/bin/python3

from functools import wraps
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from queries import *
from models import *
from config import Config
from ldap_authenticate import authenticate


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(ldap_user_id):
    return LdapUser.query.get(int(ldap_user_id))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def default():
    return render_template('index.html', events=get_events(), 
                          users=get_users(), total=get_total_paid(), 
                           total_event=count_events(),
                           total_unpaid=get_total_unpaid(),
                           user=sort_users_by_unpaid()[0])


@app.route("/pay")
@login_required
def remboursement():
    return render_template('pay.html')


@app.route("/event/<id>")
@login_required
def event(id):
    event = get_event_with_username(id)
    return render_template('event.html', event=event)


@app.route("/user/<id>")
@login_required
def user(id):
    user = get_user_with_eventname(id)
    return render_template('user.html', user=user)


@app.route("/update_transaction/<referrer>/<id_referrer>/<id>")
@login_required
def update_transaction(referrer, id_referrer, id):
    if referrer in ['user', 'event']:
        update_transaction_status(id)
        return redirect(f'/{referrer}/{id_referrer}')
    else:
        abort(404)


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    login = request.form['inputLogin']
    password = request.form['inputPassword']
    if authenticate(login, password):
        ldap_user = LdapUser.query.filter_by(login=login).first()
        if ldap_user is None:
            ldap_user = LdapUser(login=login, is_admin=False)
            db.session.add(ldap_user)
            db.session.commit()
            ldap_user = LdapUser.query.filter_by(login=login).first()
        flash('Authentification effectuée avec succès.', 'success')
        login_user(ldap_user)
        return redirect('/')
    else: 
        flash('Echec de l\'authentification.', 'error')
        return render_template('login.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/login')

@app.errorhandler(404)
def error404(error): 
    flash(str(error), 'error')
    return redirect(url_for('default'))


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=8154, debug=True)
