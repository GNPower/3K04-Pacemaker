import pytest, os, sys, inspect, logging
from flask import session
from multiprocessing import Process

thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentfolder = os.path.dirname(thisfolder)
sys.path.insert(0, parentfolder)

import app
from data.database import *
from data.user import *
from config.config_manager import *

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
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = create_db()
    assert len(results) == 2
    assert type(results[0]) == sqlite3.Connection
    assert type(results[1]) == sqlite3.Cursor

def test_user_insertion_and_search():
    logging.getLogger().info('Test User Insertion And Search:')
    logging.getLogger().info('\tThis test ensures that users can be inserted into and searched for in a database')
    logging.getLogger().info('\tExpecting successful function return from creating user (testuser, test_password)')
    logging.getLogger().info('\tExpecting a list cnotaining a correctly initialized single user and None intitialized pacemaker parameters from search for user (testuser, test_password)')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = create_db()
    insert_user(results[0], results[1], 'testuser', 'test_password')
    users = find_user(results[1], username='testuser', password='test_password')
    assert users[0][0] == 1
    assert users[0][1] == 'testuser'
    assert users[0][2] == 'test_password'

def test_get_user():
    logging.getLogger().info('Test Get User:')
    logging.getLogger().info('\tThis test ensure that users can be found in the database when searched for by their known unique ID')
    logging.getLogger().info('\tExpecting a list containing the same user as previously created (1, testuser, test_password) when searching for users with unique ID of 1')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = create_db()
    insert_user(results[0], results[1], 'testuser', 'test_password')
    users = get_user(results[1], 1)
    assert users[0] == 1
    assert users[1] == 'testuser'
    assert users[2] == 'test_password'

def test_get_rows():
    logging.getLogger().info('Test Get Rows:')
    logging.getLogger().info('\tThis test ensures the database has the correct number of rows and is capable of returning that number')
    logging.getLogger().info('\tExpecting 5 rows returned after creating a new db and inserting exactly 5 users')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = create_populated_db()
    rows = get_rows(results[1])
    assert rows == 5

def test_parameter_update():
    logging.getLogger().info('Test Parameter Update:')
    logging.getLogger().info('\tThis test ensures previously created users can have their parameters updated successfully')
    logging.getLogger().info('\tExpecting a user with updated parameters (67, 43, 44, 45, 87, 56, 89, 90) after creating new user and changing their parameters to (67, 43, 44, 45, 87, 56, 89, 90)')
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
    
def test_config_initializes():
    logging.getLogger().info('Test Config Initializes:')
    logging.getLogger().info('\tThis test ensures the config module can create a config handler containing the correct information when given a config file with known contents')
    logging.getLogger().info('\tExpecting logger.level == DEBUG && db.local-uri == db_test_name_variable')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    results = Config.getInstance()
    assert results.get('Logging', 'logger.level') == 'DEBUG'
    assert results.get('Database', 'db.local-uri') == test_db_name
    assert results.get('Applictation', 'app.secret-key')

def test_user_initializes():
    logging.getLogger().info('Test User Initializes:')
    logging.getLogger().info('\tThis test ensures a user can be created, and that the created user properly initializes their dependencies (database)')
    logging.getLogger().info('\tExpecting a user containing active connection and cursor handlers to a database matching the test_config specifications')
    create_test_config()
    init_config_and_logger(cfg_files=[test_config_name])
    create_db()
    user = User()
    assert user



def test_login_acessable():
    logging.getLogger().info('Test Login Accessable:')
    logging.getLogger().info('\tThis test ensures that the login state is acessable when the DCM is first created')
    logging.getLogger().info('\tExpecting a rendered login page')
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

def test_login_populated():
    logging.getLogger().info('Test Login Populated:')
    logging.getLogger().info('\tThis test checks that the rendered login state has rendered the expected content')
    logging.getLogger().info('\tExpecting a rendered login page matching the home directory index.hmtl')
    app.app.testing = True
    with app.app.test_client() as client:
        response = client.get('/', content_type='html/text')
        assert b'Click Here To Login' in response.data

def test_login_correct():
    logging.getLogger().info('Test Login Correct:')
    logging.getLogger().info('\tThis test checks that when a login attempt is made using the correct username and password that DCM access is granted')
    logging.getLogger().info('\tExpecting state change to logged in and the user specific page is rendered and matching that of user.html')
    app.app.testing = True
    with app.app.test_client() as client:
        response = client.post('/', data=dict(username='test_user_2', password='test_password_2'), follow_redirects=True)
        assert b'You were just logged in!' in response.data

def test_login_incorrect():
    logging.getLogger().info('Test Login Incorrect:')
    logging.getLogger().info('\tThis test checks that when a login attempt is made using incorrect parameters that login is denied and the user is informed')
    logging.getLogger().info('\tExpecting no state change and the user is flashed with an Invalid Credentials message')
    app.app.testing = True
    with app.app.test_client() as client:
        response = client.post('/', data=dict(username='baduser', password='badpass'), follow_redirects=True)
        assert b'Invalid credentials. Please try agian.' in response.data

def test_logout():
    logging.getLogger().info('Test Logout:')
    logging.getLogger().info('\tThis test ensures that if a logged in user attempts to logout that the logout is handled correctly and they are actually logged out')
    logging.getLogger().info('\tExpecting a state change to home and the home page is rendered and matching that of index.html')
    logging.getLogger().info('\tExpecting the user is flashed with the correct logout message')
    app.app.testing = True
    with app.app.test_client() as client:
        client.post('/', data=dict(username='test_user_2', password='test_password_2'), follow_redirects=True)
        response = client.get('/logout', follow_redirects=True)
        assert b'You were just logged out!' in response.data

def test_user_route_blocked():
    logging.getLogger().info('Test User Route Blocked:')
    logging.getLogger().info('\tThis test checks that when no user is logged in that all user specific pages are blocked and access to a users data is denied')
    logging.getLogger().info('\tExpecting no state change and the user is flashed with a You Need To Login First message')
    app.app.testing = True
    with app.app.test_client() as client:
        response = client.get('/user', follow_redirects=True)
        assert b'You need to login first.' in response.data

def test_user_pages_acessable():
    logging.getLogger().info('Test User Pages Acessible:')
    logging.getLogger().info('\tThis test ensures that when a user is logged in they are able to access every user specific page and their parameters')
    logging.getLogger().info('\tExpecting all state change attempts accepted and all user specific pages rendered on request')
    app.app.testing = True
    with app.app.test_client() as client:
        client.post('/', data=dict(username='test_user_2', password='test_password_2'), follow_redirects=True)

        response = client.get('/user')
        assert response.status_code == 200
        
        response = client.get('/user/parameters')
        assert response.status_code == 200

        response = client.get('/user/connect')
        assert response.status_code == 200