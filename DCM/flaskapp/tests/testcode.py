import os, inspect, sys, datetime, time, random, string, glob, shutil
import serial.tools.list_ports
from string import ascii_lowercase
from random import choice

from time import sleep

thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentfolder = os.path.dirname(thisfolder)
sys.path.insert(0, parentfolder)

from data.database import *
from config.config_manager import *
from data.user import *
from graphs.graphing import *

import app

test_db_name = 'test_db.db'
test_config_name = 'test.ini'

def create_db():
    if os.path.exists('{0}/../data/{1}'.format(thisfolder, test_db_name)):
        os.remove('{0}/../data/{1}'.format(thisfolder, test_db_name))
    return init_db(test_db_name)

def create_populated_db():
    if os.path.exists('{0}/../data/{1}'.format(thisfolder, test_db_name)):
        os.remove('{0}/../data/{1}'.format(thisfolder, test_db_name))  
    db = init_db(test_db_name)
    for user in range(1,6):
        username = 'test_user_' + str(user)
        passowrd = 'test_password_' + str(user)
        insert_user(db[0], db[1], username, passowrd)
    return db


def create_populated_filled_db():
    if os.path.exists('{0}/../data/{1}'.format(thisfolder, test_db_name)):
        os.remove('{0}/../data/{1}'.format(thisfolder, test_db_name))  
    db = init_db(test_db_name)
    for user in range(1,11):
        username = 'test_user_' + str(user)
        passowrd = 'test_password_' + str(user)
        insert_user(db[0], db[1], username, passowrd)
    return db

def create_test_config():
    if os.path.exists('{0}/../config/{1}'.format(thisfolder, test_config_name)):
        os.remove('{0}/../config/{1}'.format(thisfolder, test_config_name))
    config = open('{0}/../config/{1}'.format(thisfolder, test_config_name), 'w')
    config.write('[Logging]\n\tlogger.level=DEBUG\n\n[Database]\n\tdb.local-uri={0}'.format(test_db_name))
    config.close()

def init_config_and_logger(cfg_files=[]):
    cfg = Config.getInstance()
    cfg.reset_config()
    cfg.read_config(cfg_files)

    lgr = Logger.getInstance()
    lgr.reset_logger()
    lgr.start_logger(cfg)


user = User()

print(json.dumps(user.get_pacemaker_parameters(), indent=4, sort_keys=False))
nones = not any(user.get_pacemaker_parameters().values())
print(nones)

sorted((minval, value, maxval))[1]