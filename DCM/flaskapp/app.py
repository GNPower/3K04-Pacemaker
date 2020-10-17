from flask import Flask, render_template, redirect, url_for, request, session, flash
from threading import Timer
import webbrowser

from config.config_manager import init_logging, init_config
from config.decorators import login_required


config = init_config()
logger = init_logging(config)
logger.info('testing...')
app = Flask(__name__)

app.secret_key = "Ld5Nmcjx7lqdPbGVCxrb"

@app.route('/')
def home():
    logger.debug('this is a debug log')
    return render_template('index.html')

@app.route('/user')
@login_required
def user():
    return render_template('user.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid credentials. Please try agian.'
        else:
            session['logged_in'] = True
            flash('You were just logged in!')
            return redirect(url_for('user'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('home'))


def open_browser():
    webbrowser.open_new('http://' + config.get('HostSelection','host.address') + ':' + config.get('HostSelection', 'host.port') + "/")

if __name__ == '__main__':
    Timer(1, open_browser).start()
    #WARNING: Change 'use_reloader' and 'debug' to False before shipping release
    app.run(debug=True, host=config.get('HostSelection', 'host.address'), port=config.get('HostSelection', 'host.port'), use_reloader=True)