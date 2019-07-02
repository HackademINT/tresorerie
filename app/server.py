#!/usr/bin/python3

from functools import wraps
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from queries import *
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/")
def default():
    return render_template('index.html', events=get_events(), 
                          users=get_users(), total=get_total_paid(), 
                           total_event=count_events(),
                           total_unpaid=get_total_unpaid(),
                           user=sort_users_by_unpaid()[0])


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


@app.route("/update_transaction/<referrer>/<id_referrer>/<id>")
def update_transaction(referrer, id_referrer, id):
    if referrer in ['user', 'event']:
        update_transaction_status(id)
        return redirect(f'/{referrer}/{id_referrer}')
    else:
        abort(404)


@app.errorhandler(404)
def erreur404(error): 
    flash(str(error), 'error')
    return redirect(url_for('default'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8154, debug=True)
