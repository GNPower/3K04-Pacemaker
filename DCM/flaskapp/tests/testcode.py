import pytest, os, sys, inspect, sqlite3
from flask import request

thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentfolder = os.path.dirname(thisfolder)
sys.path.insert(0, parentfolder)

#from app import app
from data.database import *
from data.user import *
from config.config_manager import *
import app

def create_db():
    if os.path.exists('{}/../data/test_db.db'.format(thisfolder)):
        os.remove('{}/../data/test_db.db'.format(thisfolder))  
    return init_db('test_db.db')


def create_populated_db():
    if os.path.exists('{}/../data/test_db.db'.format(thisfolder)):
        os.remove('{}/../data/test_db.db'.format(thisfolder))  
    db = init_db('test_db.db')
    for user in range(1,6):
        username = 'test_user_' + str(user)
        passowrd = 'test_password_' + str(user)
        insert_user(db[0], db[1], username, passowrd)
    return db


def create_populated_filled_db():
    if os.path.exists('{}/../data/test_db.db'.format(thisfolder)):
        os.remove('{}/../data/test_db.db'.format(thisfolder))  
    db = init_db('test_db.db')
    for user in range(1,11):
        username = 'test_user_' + str(user)
        passowrd = 'test_password_' + str(user)
        insert_user(db[0], db[1], username, passowrd)
    return db

def create_test_config():
    if os.path.exists('{}/../config/test.ini'.format(thisfolder)):
        os.remove('{}/../config/test.ini'.format(thisfolder))
    config = open('{}/../config/test.ini'.format(thisfolder), 'w')
    config.write('[Logging]\n\tlogger.level=DEBUG\n\n[Database]\n\tdb.local-uri=test_db.db')
    config.close()


create_test_config()
create_populated_db()
test_config = init_config('test.ini')
test_user = User(test_config)

app.app.testing = True
with app.app.test_client() as client:
    app.config = test_config
    app.logger = init_logging(test_config)
    app.user = test_user
    
    client.post('/', data=dict(username='test_user_2', password='test_password_2'), follow_redirects=True)

    response = client.get('/user')
    print(response.status_code)
    
    response = client.get('/user/parameters')
    print(response.status_code)

    response = client.get('/user/connect')
    print(response.status_code)

    
    

# from PIL import Image
# import io, hashlib

# image = Image.open('C:/Users/Graham/Downloads/thankyourandomcitizen.jpg')
# output = io.BytesIO()
# image.save(output, format="jpeg")
# words = output.getvalue()
# print(len(words))
# myhash = hashlib.sha1(str(words).encode("UTF-8")).hexdigest()
# print(myhash)
# print(myhash[:4])