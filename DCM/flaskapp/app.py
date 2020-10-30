"""
Main Application
-------------------------
The main implementation of the DCM flaskapp. 
Handles rendering off all the endpoints as well 
as communication between the frontend and 
backend.
"""


from flask import Flask, render_template, redirect, url_for, request, session, flash
from threading import Timer
import webbrowser
import sqlite3

from config.config_manager import init_logging, init_config
from config.decorators import login_required, logout_required
from data.user import User
from data.database import init_db


#initialize the config and logger before createing the app
config = init_config()
logger = init_logging(config)
#create the user
user = User(config)
#create the flask app, passing this file as the main, and a random string as the secret key
app = Flask(__name__)
#app.secret_key = "Ld5Nmcjx7lqdPbGVCxrb"
app.secret_key = config.get('Applictation', 'app.secret-key')


@app.route('/', methods=['GET', 'POST'])
@logout_required
def home():
    """home The route to the homepage of the flask application

    Renders the homepage of the flask app and manages post requests. 
    Supported post request are 'login' and 'account creation' requests, 
    which when completed successfully will redirect the user to their 
    user specific page. Any failed post request will result in an error 
    message flashed to the screen.

    :return: The render template used by the homepage, in this case the 'index.html' template
    :rtype: :class:`flask.render_tmeplate`
    """
    error = None
    #if a POST method then either a user is loggin in or being created
    if request.method == 'POST':
        #print(request.form)
        #if post has 3 entries, a user is being created
        if (len(request.form) > 2):
            #ensure password and confirm-passwords match, if they do try to create an account
            if(request.form['password'] == request.form['confirmpassword']):
                result = user.create_account(
                    request.form['username'], request.form['password'])
                #If account creation returns True, the user was created and logged in
                if result:
                    #take them to their user specific page
                    return redirect(url_for('user_page'))
                #if it returns False, their was some sort of error
                else:
                    error = 'An error occured when creating the account!\nThe account may already exists, or the 10 user local limit has been reached'
            #if passwords dont match, throw an error and cancel the account creation
            else:
                error = 'passwords don\'t match. Could not create new account'
        #if post has 2 entries, a user is logging in
        else:
            #print('calling login')
            #attempts to log the user in
            user.login(request.form['username'], request.form['password'])            
            #print('login completed')
            #if the user was logged in, redirect them to their user specific page
            if user.is_loggedin():
                flash('You were just logged in!')
                return redirect(url_for('user_page'))
            #if an error occured, let them know
            else:
                error = 'Invalid credentials. Please try agian.'
    return render_template('index.html', error=error)


@app.route('/user')
@login_required
def user_page():
    """user_page The route to the user specific page of the flask application

    Renders the user specific page of the flask app. This page acts as an intermediary 
    between the 'login' state and any other states which require login, such as the 
    user parameters and pacing mode specific states.

    :return: The render template used by the user specific page, in this case the 'user.html' template
    :rtype: :class:`flask.render_tmeplate`
    """
    return render_template('user.html')


@app.route('/user/parameters', methods=['GET', 'POST'])
@login_required
def user_parameters():
    """user_parameters The route to the user parameters page of the flask application

    Renders the user parameters page of the flask app. This page allows the user to 
    view and modify their pacemaker parameters through a submittable form. Users can 
    modify some or all parameters and submit the changes through a post request. Changes 
    will be made immediately in the flask app and database, and the user parameters page 
    updated with these changed values.

    :return: The render template used by the user parameters page, in this case the 'user_parameters.html' template
    :rtype: :class:`flask.render_tmeplate`
    """
    #if a post request is made, a user is trying to change their parameters
    if request.method == 'POST':
        #print('FORM:', request.form)
        #create a new parameters dictionary by starting with the original dictionary, and updating its values with the modified value from the post request
        updates = {j: {k: v for k, v in dict(request.form).items() if v}.get(j, user.get_pacemaker_parameters()[j]) for j in user.get_pacemaker_parameters()}
        #print('UPDATES:', updates)
        #updates all the pacemaker parameters with the newly generated list
        user.update_all_pacemaker_parameters(updates)
    return render_template('user_parameters.html', username=user.get_username(), parameters=user.get_pacemaker_parameters())


@app.route('/user/connect', methods=['GET', 'POST'])
@login_required
def user_connect():
    """user_connect The route to the user connect page of the flask application

    Renders the user connect page of the flask app. This page allows the user to 
    view the status of the pacemaker in different pacing modes. Pacing modes can 
    be changed via a selection box at the top of the page. NOTE: This page will 
    correctly change between different pacing mode states, though these states 
    and their corresponding rendered templates are black as no serial communication 
    with the pacemaker has been implemented. As a result changing modes will have little 
    visible effect on the rendered content of the application.

    :return: The render template used by the user connect page, in this case the 'user_connect.html' template
    :rtype: :class:`flask.render_tmeplate`
    """
    #sets the default pacemaker mode to 'None', forcing the user to select a mode manually
    #This is an attempt to avoid the user programming the pacemaker in a mode they did not intend
    mode = 'None'
    if request.method == 'POST':
        #print(request.form['Pacing Mode'])
        #Flashes the new pacing mode to the user to let them know the applications state has changed
        flash('Pacing Mode Changed To {0}'.format(request.form['Pacing Mode']))
        #changes the pacing mode (i.e. the application state)
        mode = request.form['Pacing Mode']
    return render_template('user_connect.html', mode=mode)


@app.route('/logout')
@login_required
def logout():
    """logout The route to the logout page of the flask application

    This page acts as an intermediary between a user page that requires login 
    and the homepage of this application. This page logs the user out and  
    immediately redirects to the homepage, flashing a logout message after 
    the redirect.

    :return: A redirect to the homepage of the application
    :rtype: :class:`flask.redirect`
    """
    #logg the user out
    user.logout()
    #redirects to the home screen and flashes a logout message
    flash('You were just logged out!')
    return redirect(url_for('home'))


def open_browser():
    """open_browser Opens the flask app automatically in the web brower.

    So the user doesn't have to memorize the url and port the application 
    is being hosted on.
    """
    webbrowser.open_new('http://' + config.get('HostSelection', 'host.address') +
                        ':' + config.get('HostSelection', 'host.port') + "/")


if __name__ == '__main__':
    #calls the open_browser function in a new thread to avoid interfering with the application startup
    if config.get('Applictation', 'app.open-on-load'):
        Timer(1, open_browser).start()
    # WARNING: Change 'use_reloader' and 'debug' to False before shipping release (done in the application.ini file)
    app.run(debug=config.getboolean('Applictation', 'app.debug'), host=config.get('HostSelection', 'host.address'), port=config.get(
        'HostSelection', 'host.port'), threaded=config.getboolean('Applictation', 'app.threaded'), use_reloader=config.getboolean('Applictation', 'app.use-reloader'))