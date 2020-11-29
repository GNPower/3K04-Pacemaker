import pytest, os, sys, inspect, logging, random, string, glob
from flask import session
from multiprocessing import Process
from time import sleep
from string import ascii_lowercase
from random import choice, randint

thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentfolder = os.path.dirname(thisfolder)
sys.path.insert(0, parentfolder)

import app
from data.database import *
from data.user import *
from config.config_manager import *
from graphs.graphing import *

test_db_name = 'test_db.db'
test_config_name = 'test.ini'

def test_pytest_functional():
    logging.getLogger().setLevel('DEBUG')
    logging.getLogger().info('Initializing PyTest module and ensuring its functionality')
    assert 0 == 0

def create_db():
    logging.getLogger().info('Creating empty testing database')
    if os.path.exists('{0}/../data/{1}'.format(thisfolder, test_db_name)):
        os.remove('{0}/../data/{1}'.format(thisfolder, test_db_name))
    return init_db(test_db_name)

def create_populated_db():
    logging.getLogger().info('Creating partially populated testing database')
    if os.path.exists('{0}/../data/{1}'.format(thisfolder, test_db_name)):
        os.remove('{0}/../data/{1}'.format(thisfolder, test_db_name))  
    db = init_db(test_db_name)
    for user in range(1,6):
        username = 'test_user_' + str(user)
        passowrd = 'test_password_' + str(user)
        insert_user(db[0], db[1], username, passowrd)
    return db


def create_populated_filled_db():
    logging.getLogger().info('Creating filled database')
    if os.path.exists('{0}/../data/{1}'.format(thisfolder, test_db_name)):
        os.remove('{0}/../data/{1}'.format(thisfolder, test_db_name))  
    db = init_db(test_db_name)
    for user in range(1,11):
        username = 'test_user_' + str(user)
        passowrd = 'test_password_' + str(user)
        insert_user(db[0], db[1], username, passowrd)
    return db

def rm_db(conn):
    shutdown_db(conn)
    logging.getLogger().info('Test complete, removing test database')
    if os.path.exists('{0}/../data/{1}'.format(thisfolder, test_db_name)):
        os.remove('{0}/../data/{1}'.format(thisfolder, test_db_name))  

def create_test_config():
    logging.getLogger().info('Overriding default config with test values')
    if os.path.exists('{0}/../config/{1}'.format(thisfolder, test_config_name)):
        os.remove('{0}/../config/{1}'.format(thisfolder, test_config_name))
    config = open('{0}/../config/{1}'.format(thisfolder, test_config_name), 'w')
    config.write('[Logging]\n\tlogger.level=DEBUG\n\n[Database]\n\tdb.local-uri={0}'.format(test_db_name))
    config.close()

def init_config_and_logger(cfg_files=[]):
    logging.getLogger().info('Initializing test Config manager and Logger')
    cfg = Config.getInstance()
    cfg.reset_config()
    cfg.read_config(cfg_files)
    lgr = Logger.getInstance()
    lgr.reset_logger()
    lgr.start_logger(cfg)

def test_db_initialization(): 
    logging.getLogger().info('Test DB Initialization:')
    logging.getLogger().info('\tThis test ensures the Database Library can create a new database and that it can load an existing one')
    logging.getLogger().info('\tExpecting active sqlite3 connection and cursor handlers are returned by this test')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-DBS-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = create_db()
    assert len(results) == 2
    assert type(results[0]) == sqlite3.Connection
    assert type(results[1]) == sqlite3.Cursor
    rm_db(results[0])

def test_user_insertion_and_search():
    logging.getLogger().info('Test User Insertion And Search:')
    logging.getLogger().info('\tThis test ensures that users can be inserted into and searched for in a database')
    logging.getLogger().info('\tExpecting successful function return from creating user (testuser, test_password)')
    logging.getLogger().info('\tExpecting a list cnotaining a correctly initialized single user and None intitialized pacemaker parameters from search for user (testuser, test_password)')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-DBS-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = create_db()
    insert_user(results[0], results[1], 'testuser', 'test_password')
    users = find_user(results[1], username='testuser', password='test_password')
    assert users[0][0] == 1
    assert users[0][1] == 'testuser'
    assert users[0][2] == 'test_password'
    rm_db(results[0])

def test_get_user():
    logging.getLogger().info('Test Get User:')
    logging.getLogger().info('\tThis test ensure that users can be found in the database when searched for by their known unique ID')
    logging.getLogger().info('\tExpecting a list containing the same user as previously created (1, testuser, test_password) when searching for users with unique ID of 1')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-DBS-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = create_db()
    insert_user(results[0], results[1], 'testuser', 'test_password')
    users = get_user(results[1], 1)
    assert users[0] == 1
    assert users[1] == 'testuser'
    assert users[2] == 'test_password'
    rm_db(results[0])

def test_get_rows():
    logging.getLogger().info('Test Get Rows:')
    logging.getLogger().info('\tThis test ensures the database has the correct number of rows and is capable of returning that number')
    logging.getLogger().info('\tExpecting 5 rows returned after creating a new db and inserting exactly 5 users')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-DBS-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = create_populated_db()
    rows = get_rows(results[1])
    assert rows == 5
    rm_db(results[0])

def test_parameter_update():
    logging.getLogger().info('Test Parameter Update:')
    logging.getLogger().info('\tThis test ensures previously created users can have their parameters updated successfully')
    logging.getLogger().info('\tExpecting a user with updated parameters (67, 43, 44, 45, 87, 56, 89, 90) after creating new user and changing their parameters to (67, 43, 44, 45, 87, 56, 89, 90)')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-DBS-REQ-02')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = create_populated_db()
    initial = get_user_parameters(results[1], 3)
    for value in initial[2:]:
        assert value == None
    update_pacemaker_parameters(results[0], results[1], 3, ['VVI', 43, 44, 45, 56, 67, 89, 87, 90, 34, 46, 64, 93, 56, 86, 24 ,65, 23, 74, 35])
    updates = get_user_parameters(results[1], 3)
    assert updates[1] == 'current'
    assert updates[2:] == ('VVI', 43, 44, 45, 56, 67, 89, 87, 90, 34, 46, 64, 93, 56, 86, 24 ,65, 23, 74, 35)
    rm_db(results[0])

def test_parameter_history():
    logging.getLogger().info('Test Parameter History:')
    logging.getLogger().info('\tThis test ensures previously created users can have thier history stored and retrieved succressfully')
    logging.getLogger().info('\tWill generate 6 different parameter updates with random values and modes and ensure that the history returned contains the same parameters updates with the same values in the same order')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-DBS-REQ-03')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = create_populated_db()
    initial = get_user_parameters(results[1], 3)
    for value in initial[2:]:
        assert value == None
    updates_sqeuence = []
    allowed_modes = ['AOO','VOO','AAI','VVI','DOO','AOOR','VOOR','AAIR','VVIR','DOOR']
    for i in range(0,6):
        update_i = [choice(allowed_modes)]
        for j in range(0,19):
            update_i.append(randint(1,100))
        updates_sqeuence.append(update_i)
    for update in updates_sqeuence:
        update_pacemaker_parameters(results[0], results[1], 3, update)
    history = get_user_history(results[1], 3)
    for index,value in enumerate(history):
        assert tuple(updates_sqeuence[index]) == value[2:]
    rm_db(results[0])
    
    
def test_config_initializes():
    logging.getLogger().info('Test Config Initializes:')
    logging.getLogger().info('\tThis test ensures the config module can create a config handler containing the correct information when given a config file with known contents')
    logging.getLogger().info('\tExpecting logger.level == DEBUG && db.local-uri == db_test_name_variable')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-CFG-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = Config.getInstance()
    assert results.get('Logging', 'logger.level') == 'DEBUG'
    assert results.get('Database', 'db.local-uri') == test_db_name
    assert results.get('Applictation', 'app.secret-key')

def test_config_parameters_available():
    logging.getLogger().info('Test Config Parameters Available:')
    logging.getLogger().info('\tThis test ensures that a list of all config parameters are made available by the Config Manager')
    logging.getLogger().info('\tExpecting a list of pacemaker parameters matching both the list in the .ini file and the PACEMAKER.pdf requirements document')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-CFG-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    vals = Config.getInstance().get('Parameters', 'parameters.values').split(',')
    assert vals == ['Lower Rate Limit', 'Upper Rate Limit', 'Atrial Amplitude', 'Atrial Pulse Width', 'Atrial Refractory Period', 'Atrial Sensitivity', 'Ventricular Amplitude', 'Ventricular Pulse Width', 'Ventricular Refractory Period', 'Ventricular Sensitivity', 'Post Ventricular Atrial Refractory Period', 'Hysterysis', 'Rate Smoothing', 'Fixed AV Delay', 'Maximum Sensor Rate', 'Activity Threshold', 'Reaction Time', 'Response Factor', 'Recovery Time']

def test_config_modes_available():
    logging.getLogger().info('Test Config Mode Available:')
    logging.getLogger().info('\tThis test ensures that a list of all config mode are made available by the Config Manager')
    logging.getLogger().info('\tExpecting a list of pacemaker modes matching both the list in the .ini file and the PACEMAKER.pdf requirements document')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-CFG-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    vals = Config.getInstance().get('Parameters', 'parameters.modes').split(',')
    assert vals == ['AOO', 'VOO', 'AAI', 'VVI', 'DOO', 'AOOR', 'VOOR', 'AAIR', 'VVIR', 'DOOR']

def test_config_mode_matches_available():
    logging.getLogger().info('Test Config Mode-Parameters Matched Available:')
    logging.getLogger().info('\tThis test ensures that the list of parameters allowed for each pacemaker mode are made available by the Config Manager')
    logging.getLogger().info('\tExpecting a list for every pacemaker mode containing the parameters used in that modes is available and matches both the lists in the .ini file and the PACEMAKER.pdf requirements document')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-CFG-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    params = Config.getInstance().get('Parameters', 'parameters.values').split(',')
    modes = Config.getInstance().get('Parameters', 'parameters.modes').split(',')
    for mode in modes:
        matches = Config.getInstance().get('Parameters', 'parameters.mode.' + str(mode)).split(',')
        check = all(item in params for item in matches)
        assert check == True

def test_config_mode_limits_available():
    logging.getLogger().info('Test Config Mode Limits Available:')
    logging.getLogger().info('\tThis test ensures that the list of limits on each parameter are made available by the Config Manager')
    logging.getLogger().info('\tExpecting a series of lists detailing all the limits on individual parameters that matches both the .ini file and the PACEMAKER.pdf requrements document')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-CFG-REQ-02')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    limits = Config.getInstance().get_all('Limits')
    assert limits == [('limits.atrial amplitude', '0.1,5.0,0.1'), ('limits.can-disable.atrial amplitude', 'True'), ('limits.ventricular amplitude', '0.1,5.0,0.1'), ('limits.can-disable.ventricular amplitude', 'True'), ('limits.atrial pulse width', '1,30,1'), ('limits.ventricular pulse width', '1,30,1'), ('limits.atrial sensitivity', '0.0,5.0,0.1'), ('limits.ventricular sensitivity', '0.0,5.0,0.1')]

def test_config_egram_params_available():
    logging.getLogger().info('Test Config Egram Params Available:')
    logging.getLogger().info('\tThis test ensures that the egram parameters outlined in the config are made available by the Config Manager')
    logging.getLogger().info('\tExpecting a series of variables that matches both the .ini file and the Assignment2.pdf requirements document')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-CFG-REQ-03')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    egrams = Config.getInstance().get_all('Graphing')
    assert egrams == [('graph.domain', '1000'), ('graph.update-period', '5'), ('graph-export-style', 'fivethirtyeight')]

def test_config_log_params_available():
    logging.getLogger().info('Test Config Logging Params Available:')
    logging.getLogger().info('\tThis test ensures that the logging parameters outlines in the config are made available by the Config Manager')
    logging.getLogger().info('\tExpecting a series of variables that matches the .ini file')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-CFG-REQ-04')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    logs = Config.getInstance().get_all('Logging')
    assert logs == [('logger.level', 'DEBUG'), ('logger.file-prefix', 'FLASKAPP-'), ('logger.date-format', '%Y-%m-%d-%H.%M.%S'), ('logger.log-format', '%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')]

def test_user_initializes():
    logging.getLogger().info('Test User Initializes:')
    logging.getLogger().info('\tThis test ensures a user can be created, and that the created user properly initializes their dependencies (database)')
    logging.getLogger().info('\tExpecting a user containing active connection and cursor handlers to a database matching the test_config specifications')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-USR-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    create_db()
    user = User()
    assert user

def test_user_parameters_available():
    logging.getLogger().info('Test User Parameters Available:')
    logging.getLogger().info('\tThis test ensures a users parameters are initialized to None by default, and that all their parameters are made available to the FlaskApp on request')
    logging.getLogger().info('\tExpecting a user response containing a list of its parameters, all of which have a None value')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-USR-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    user = User()
    params = user.get_pacemaker_parameters()
    assert len(params) == 19
    for vlaue in params.values():
        assert vlaue == None

def test_user_limits_available():
    logging.getLogger().info('Test User Limits Available:')
    logging.getLogger().info('\tThis test ensures the limits outlined in the config are stored properly by the user and made available on request to the FlaskApp')
    logging.getLogger().info('\tExpecting a dictionary of parameter limits whos values match those outlines in the .ini configuration file')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-USR-REQ-03')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    user = User()
    limits = user.get_limits()
    assert limits == {'Atrial Amplitude': {'min': 0.1, 'max': 5.0, 'inc': 0.1, 'can_disable': True}, 'Atrial Pulse Width': {'min': 1.0, 'max': 30.0, 'inc': 1.0}, 'Atrial Sensitivity': {'min': 0.0, 'max': 5.0, 'inc': 0.1}, 'Ventricular Amplitude': {'min': 0.1, 'max': 5.0, 'inc': 0.1, 'can_disable': True}, 'Ventricular Pulse Width': {'min': 1.0, 'max': 30.0, 'inc': 1.0}, 'Ventricular Sensitivity': {'min': 0.0, 'max': 5.0, 'inc': 0.1}}

def test_user_login_works():
    logging.getLogger().info('Test User Login Works:')
    logging.getLogger().info('\tThis test ensures that the user model is capable of correctly logging in a user given a correct set of cedentials')
    logging.getLogger().info('\tExpecting a return value of True from both the login method and the sLoggedIn method to indicate the user was logged in correctly and their login can be verified respectively')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-USR-REQ-04')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    create_populated_db()
    test_user = User()
    app.app.testing = True
    with app.app.test_client() as client:
        app.user = test_user
        response = client.get('/', content_type='html/text')
        app.user.login('test_user_2', 'test_password_2')
        result = app.user.is_loggedin()
        assert result == True
        rm_db(app.user.get_db_handlers()[0])

def test_user_creation_works():
    logging.getLogger().info('Test User Creation Works:')
    logging.getLogger().info('\tThis test ensures that the user model can create a new user given a unique and never before used set of credentials')
    logging.getLogger().info('\tExpecting a return type of True to indicate a new user was successfully created and logged in')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-USR-REQ-05')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    create_populated_db()
    test_user = User()
    app.app.testing = True
    with app.app.test_client() as client:
        app.user = test_user
        response = client.get('/', content_type='html/text')
        app.user.create_account('test_user_new', 'test_password_new')
        result = app.user.is_loggedin()
        assert result == True
        rm_db(app.user.get_db_handlers()[0])

def test_user_creation_denied_on_full_db():
    logging.getLogger().info('Test User Creation Denied On Full Database')
    logging.getLogger().info('\tThis test ensures that if the database in use by the application is full that the user model will deny the creation of a new account given a set of credentials which for every other reason should work in creating a new account')
    logging.getLogger().info('\tExpecting a return value of False from the method to indicate an error in the account creation')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-USR-REQ-06')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    create_populated_filled_db()
    test_user = User()
    app.app.testing = True
    with app.app.test_client() as client:
        app.user = test_user
        response = client.get('/', content_type='html/text')
        result = app.user.create_account('test_user_new', 'test_password_new')
        assert result == False
        rm_db(app.user.get_db_handlers()[0])

def test_user_parameter_modification():
    logging.getLogger().info('Test User Parameters Modifiable:')
    logging.getLogger().info('\tThis test ensures that the parameters stored by the user can be modified at runtime, and those modifications persist for the remainder of the applications runtime')
    logging.getLogger().info('\tExpecting a list of parameters matching the most recent list passed to the parameter update method')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-USR-REQ-02')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    create_populated_db()
    test_user = User()
    app.app.testing = True
    with app.app.test_client() as client:
        app.user = test_user
        response = client.get('/', content_type='html/text')
        app.user.create_account('test_user', 'test_pass')
        updates_sqeuence = []
        allowed_modes = ['AOO','VOO','AAI','VVI','DOO','AOOR','VOOR','AAIR','VVIR','DOOR']
        for i in range(0,6):
            update_i = [choice(allowed_modes)]
            for j in range(0,19):
                update_i.append(randint(1,100))
            updates_sqeuence.append(update_i)
        for update in updates_sqeuence:
            app.user.update_all_pacemaker_parameters(update[1:])
            app.user.update_pacemaker_mode(update[0])
        params = app.user.get_pacemaker_parameters()
        mode = app.user.get_pacemaker_mode()
        assert list(params.values()) == updates_sqeuence[-1][1:]
        assert mode == updates_sqeuence[-1][0]
        rm_db(app.user.get_db_handlers()[0])

def test_graph_data_request():
    logging.getLogger().info('Test Graph Data Request:')
    logging.getLogger().info('\tThis test ensures that real time data can be provided by the Graphing Manager on request from the DCM')
    logging.getLogger().info('\tExpecting a unique set of data points that correspond to values on a sine and cosine curve respectively, provided by the Graphing Managers test function by default if no serial communication module is enabled. And a correct set of data provided by the serial comm module if one is enabled')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-GPH-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    res = temp_serial_placeholder()
    assert len(res) == 2
    points = update_data()
    assert len(points) == 2
    assert len(points[0]) == 2
    assert len(points[1]) == 2

def test_graph_data_publish():
    logging.getLogger().info('Test Graph Data Publishes:')
    logging.getLogger().info('\tThis test ensures that the Graphing Manager is capable of successfully publishing the data from its most recent live graph on request from the DCM')
    logging.getLogger().info('\tExpecting two files to be created in the downloads directory, one a csv file and the other a pdf file')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-GPH-REQ-02 and DCM-GPH-REQ-03')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    set_start_time()
    for i in range(0,3000):
        update_data()
        sleep(0.001)
    username = ''.join(choice(ascii_lowercase) for x in range(10))
    publish_data(username)
    os.chdir(os.path.join(parentfolder, 'downloads'))
    file_list = []
    for _file in glob.glob(username + "*.csv"):
        file_list.append(_file)
    for _file in glob.glob(username + "*.pdf"):
        file_list.append(_file)
    assert len(file_list) == 2
    assert file_list[0].endswith(".csv")
    assert file_list[1].endswith(".pdf")

def test_login_acessable():
    logging.getLogger().info('Test Login Accessable:')
    logging.getLogger().info('\tThis test ensures that the login state is acessable when the DCM is first created')
    logging.getLogger().info('\tExpecting a rendered login page')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-GPH-REQ-02 and DCM-APP-REQ-08')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    create_populated_db()
    test_user = User()
    app.app.testing = True
    with app.app.test_client() as client:
        app.user = test_user
        response = client.get('/', content_type='html/text')
        print(response)
        assert response.status_code == 200
        rm_db(app.user.get_db_handlers()[0])

def test_login_populated():
    logging.getLogger().info('Test Login Populated:')
    logging.getLogger().info('\tThis test checks that the rendered login state has rendered the expected content')
    logging.getLogger().info('\tExpecting a rendered login page matching the home directory index.hmtl')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-GPH-REQ-02 and DCM-APP-REQ-08')
    app.app.testing = True
    with app.app.test_client() as client:
        response = client.get('/', content_type='html/text')
        assert b'Click Here To Login' in response.data

def test_login_correct():
    logging.getLogger().info('Test Login Correct:')
    logging.getLogger().info('\tThis test checks that when a login attempt is made using the correct username and password that DCM access is granted')
    logging.getLogger().info('\tExpecting state change to logged in and the user specific page is rendered and matching that of user.html')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-GPH-REQ-02 and DCM-APP-REQ-08')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    create_populated_db()
    test_user = User()
    app.app.testing = True
    with app.app.test_client() as client:
        app.user = test_user
        response = client.post('/', data=dict(username='test_user_2', password='test_password_2'), follow_redirects=True)
        assert b'You were just logged in!' in response.data
        rm_db(app.user.get_db_handlers()[0])

def test_login_incorrect():
    logging.getLogger().info('Test Login Incorrect:')
    logging.getLogger().info('\tThis test checks that when a login attempt is made using incorrect parameters that login is denied and the user is informed')
    logging.getLogger().info('\tExpecting no state change and the user is flashed with an Invalid Credentials message')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-GPH-REQ-02 and DCM-APP-REQ-08')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    create_populated_db()
    test_user = User()
    app.app.testing = True
    with app.app.test_client() as client:
        app.user = test_user
        response = client.post('/', data=dict(username='baduser', password='badpass'), follow_redirects=True)
        assert b'Invalid credentials. Please try agian.' in response.data
        rm_db(app.user.get_db_handlers()[0])

def test_logout():
    logging.getLogger().info('Test Logout:')
    logging.getLogger().info('\tThis test ensures that if a logged in user attempts to logout that the logout is handled correctly and they are actually logged out')
    logging.getLogger().info('\tExpecting a state change to home and the home page is rendered and matching that of index.html')
    logging.getLogger().info('\tExpecting the user is flashed with the correct logout message')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-GPH-REQ-02 and DCM-APP-REQ-08')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    create_populated_db()
    test_user = User()
    app.app.testing = True
    with app.app.test_client() as client:
        app.user = test_user
        client.post('/', data=dict(username='test_user_2', password='test_password_2'), follow_redirects=True)
        response = client.get('/logout', follow_redirects=True)
        assert b'You were just logged out!' in response.data
        rm_db(app.user.get_db_handlers()[0])

def test_user_route_blocked():
    logging.getLogger().info('Test User Route Blocked:')
    logging.getLogger().info('\tThis test checks that when no user is logged in that all user specific pages are blocked and access to a users data is denied')
    logging.getLogger().info('\tExpecting no state change and the user is flashed with a You Need To Login First message')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-GPH-REQ-02 and DCM-APP-REQ-01')
    app.app.testing = True
    with app.app.test_client() as client:
        response = client.get('/user', follow_redirects=True)
        assert b'You need to login first.' in response.data

def test_user_pages_acessable():
    logging.getLogger().info('Test User Pages Acessible:')
    logging.getLogger().info('\tThis test ensures that when a user is logged in they are able to access every user specific page and their parameters')
    logging.getLogger().info('\tExpecting all state change attempts accepted and all user specific pages rendered on request')
    logging.getLogger().info('\tThis test works toward fulfilling DCM-GPH-REQ-02 and DCM-APP-REQ-01')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    create_populated_db()
    test_user = User()
    app.app.testing = True
    with app.app.test_client() as client:
        app.user = test_user
        client.post('/', data=dict(username='test_user_2', password='test_password_2'), follow_redirects=True)
        response = client.get('/user')
        assert response.status_code == 200
        response = client.get('/user/parameters')
        assert response.status_code == 200
        response = client.get('/user/connect')
        assert response.status_code == 200
        response = client.get('/user/history')
        assert response.status_code == 200
        response = client.get('/user/egram')
        assert response.status_code == 200
        rm_db(app.user.get_db_handlers()[0])