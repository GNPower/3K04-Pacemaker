"""
Main Application
-------------------------
The main implementation of the DCM flaskapp. 
Handles rendering off all the endpoints as well 
as communication between the frontend and 
backend.
"""


from flask import Flask, render_template, redirect, url_for, request, session, flash, make_response
from threading import Timer
from time import time
from random import random
import webbrowser, sqlite3, re, json

from config.config_manager import Config, Logger
from config.decorators import login_required, logout_required
from data.user import User
from data.database import init_db
from graphs.graphing import update_data, publish_data


#initialize the config and logger before createing the app
Config()
if not Config.getInstance().is_config_read():
    Config.getInstance().read_config()
Logger()
if not Logger.getInstance().is_logger_started():
    Logger.getInstance().start_logger(Config.getInstance())
#create the user
user = User()
#create the flask app, passing this file as the main, and a random string as the secret key
app = Flask(__name__)
app.secret_key = Config.getInstance().get('Applictation', 'app.secret-key')


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
        Logger.getInstance().log('DEBUG', 'Home route HTTP Post recieved\n\tPost Contents:\t{0}'.format(request.form))
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
            #attempts to log the user in
            Logger.getInstance().log('DEBUG', 'Attempting user login with username "{0}" and password "{1}"'.format(request.form['username'], request.form['password']))
            user.login(request.form['username'], request.form['password'])            
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
        values = dict(request.form)
        required_values = Config.getInstance().get('Parameters', 'parameters.values').split(',')
        for value in required_values:
            if value not in values:
                values[value] = -1
        #create a new parameters dictionary by starting with the original dictionary, and updating its values with the modified value from the post request
        updates = {j: {k.replace(' ', ''): v for k, v in values.items() if v}.get(j, user.get_pacemaker_parameters()[j]) for j in user.get_pacemaker_parameters()}
        #updates all the pacemaker parameters with the newly generated list
        Logger.getInstance().log('DEBUG', 'Pacemaker Parameters Updated: {0}'.format(updates))
        user.update_all_pacemaker_parameters(updates.values())
    parameters = { re.sub(r"(\w)([A-Z])", r"\1 \2", k): user.get_pacemaker_parameters()[k] for k in user.get_pacemaker_parameters() }
    return render_template('user_parameters.html', username=user.get_username(), parameters=parameters, limits=user.get_limits())


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
    mode = user.get_pacemaker_mode()
    if request.method == 'POST':
        if 'Pacing Mode' in request.form:
            #print(request.form['Pacing Mode'])
            #Flashes the new pacing mode to the user to let them know the applications state has changed
            flash('Pacing Mode Changed To {0}'.format(request.form['Pacing Mode']))
            #changes the pacing mode (i.e. the application state)
            mode = request.form['Pacing Mode']
            user.update_pacemaker_mode(mode)
        else:
            values = dict(request.form)
            mode = values.pop('Mode', None)            
            #create a new parameters dictionary by starting with the original dictionary, and updating its values with the modified value from the post request
            required_values = Config.getInstance().get('Parameters', 'parameters.mode.' + str(mode)).split(',')
            for value in required_values:
                if value not in values:
                    values[value] = -1
            updates = {j: {k.replace(' ', ''): v for k, v in values.items() if v}.get(j, user.get_pacemaker_parameters()[j]) for j in user.get_pacemaker_parameters()}
            #updates all the pacemaker parameters with the newly generated list
            Logger.getInstance().log('DEBUG', 'Pacemaker Parameters Updated: {0}'.format(updates))
            user.update_all_pacemaker_parameters(updates.values())
    if mode == None:
        parameters = {}
    else:
        parameters = { re.sub(r"(\w)([A-Z])", r"\1 \2", k): user.get_pacemaker_parameters()[k] for k in [ value.replace(' ', '') for value in Config.getInstance().get('Parameters', 'parameters.mode.' + str(mode)).split(',') ] }
    modes = Config.getInstance().get('Parameters', 'parameters.modes').split(',')
    return render_template('user_connect.html', mode=mode, modes=modes, parameters=parameters, limits=user.get_limits())


@app.route('/user/history', methods=['GET', 'POST'])
@login_required
def user_history():
    """user_history The route to the user history page of the flask application

    Renders the user history page of the flask app. This page allows the user to 
    view the entire history of their pacemaker parameters in a convenient table. 
    This table can be exported to a csv file if the user wishes, which will appear 
    in the downloads file.

    :return: The render template used by the user connect page, in this case the 'user_history.html' template
    :rtype: :class:`flask.render_tmeplate`
    """
    if request.method == 'POST':
        user.create_history_file()
    parameters = { re.sub(r"(\w)([A-Z])", r"\1 \2", k): user.get_pacemaker_parameters()[k] for k in user.get_pacemaker_parameters() }
    history = user.get_history()
    return render_template('user_history.html', username=user.get_username(), parameters=parameters, history=history)


@app.route('/user/egram', methods=['GET', 'POST'])
@login_required
def user_egram():
    """user_egram The route to the user history page of the flask application

    Renders the user egram page of the flask app. This page allows the user to 
    view a live graph (or egram) of the pacemakers atrium and ventrical chambers.
    NOTE: The graph displayed is an adaptable graph and will take up to one minute 
    to adjust both the graphs domain and range values.

    :return: The render template used by the user connect page, in this case the 'user_egram.html' template
    :rtype: :class:`flask.render_tmeplate`
    """
    if request.method == 'POST':
        publish_data(user.get_username())
    domain = int(Config.getInstance().get('Graphing', 'graph.domain'))
    period = int(Config.getInstance().get('Graphing', 'graph.update-period'))
    return render_template('user_egram.html', domain=domain, period=period)


@app.route('/user/data', methods=['GET', 'POST'])
@login_required
def user_data():
    """user_data The route to the data request uri for the egram

    Will return a json response containing updated point values to 
    be added to the live graph.

    :return: A json response, containing updated point values
    :rtype: json
    """
    response = make_response(json.dumps(update_data()))
    response.content_type = 'application/json'
    return response


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
    webbrowser.open_new('http://' + Config.getInstance().get('HostSelection', 'host.address') +
                        ':' + Config.getInstance().get('HostSelection', 'host.port') + "/")


if __name__ == '__main__':
    #calls the open_browser function in a new thread to avoid interfering with the application startup
    if Config.getInstance().get('Applictation', 'app.open-on-load'):
        Timer(1, open_browser).start()
    # WARNING: Change 'use_reloader' and 'debug' to False before shipping release (done in the application.ini file)
    app.run(debug=Config.getInstance().getboolean('Applictation', 'app.debug'), host=Config.getInstance().get('HostSelection', 'host.address'), 
    port=Config.getInstance().get('HostSelection', 'host.port'), threaded=Config.getInstance().getboolean('Applictation', 'app.threaded'), 
    use_reloader=Config.getInstance().getboolean('Applictation', 'app.use-reloader'))