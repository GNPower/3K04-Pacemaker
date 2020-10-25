from flask import Flask, render_template, redirect, url_for, request, session, flash
from threading import Timer
import webbrowser
import sqlite3

from config.config_manager import init_logging, init_config
from config.decorators import login_required, logout_required
from data.user import User
from data.test_database import init_db


config = init_config()
logger = init_logging(config)
user = User(config)
app = Flask(__name__)


app.secret_key = "Ld5Nmcjx7lqdPbGVCxrb"


@app.route('/', methods=['GET', 'POST'])
@logout_required
def home():
    error = None
    if request.method == 'POST':
        print(request.form)
        if (len(request.form) > 2):
            if(request.form['password'] == request.form['confirmpassword']):
                result = user.create_account(
                    request.form['username'], request.form['password'])
                if result:
                    return redirect(url_for('user_page'))
                else:
                    error = 'An error occured when creating the account!\nThe account may already exists, or the 10 user local limit has been reached'
            else:
                error = 'passwords don\'t match. Could not create new account'
        else:
            user.login(request.form['username'], request.form['password'])
            if user.is_loggedin():
                session['logged_in'] = True
                flash('You were just logged in!')
                return redirect(url_for('user_page'))
            else:
                error = 'Invalid credentials. Please try agian.'
    return render_template('index.html', error=error)


@app.route('/user')
@login_required
def user_page():
    return render_template('user.html')


@app.route('/user/parameters', methods=['GET', 'POST'])
@login_required
def user_parameters():
    if request.method == 'POST':
        user.update_all_pacemaker_parameters({j: {k: v for k, v in dict(request.form).items() if v}.get(
            j, user.get_pacemaker_parameters()[j]) for j in user.get_pacemaker_parameters()})
    return render_template('user_parameters.html', username=user.get_username(), parameters=user.get_pacemaker_parameters())


@app.route('/user/connect')
@login_required
def user_connect():
    return render_template('user_connect.html')


@app.route('/logout')
@login_required
def logout():
    user.logout()
    flash('You were just logged out!')
    return redirect(url_for('home'))


def open_browser():
    webbrowser.open_new('http://' + config.get('HostSelection', 'host.address') +
                        ':' + config.get('HostSelection', 'host.port') + "/")


if __name__ == '__main__':
    Timer(1, open_browser).start()
    # WARNING: Change 'use_reloader' and 'debug' to False before shipping release
    app.run(debug=True, host=config.get('HostSelection', 'host.address'), port=config.get(
        'HostSelection', 'host.port'), threaded=False, use_reloader=False)
