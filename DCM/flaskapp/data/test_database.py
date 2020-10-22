from flask import Flask, jsonify
import pymongo
import uuid

"""
NOTE:   Users are expected to be returned as lists, whose entries are in the following order
        [ _userid, username, password, LowerRateLimit, UpperRateLimit, AtrialAmplitude, AtrialPulseWidth,
            AtrialRefractoryPeriod, VentricularAmplitude, VentricularPulseWidth, VentricularRefractoryPeriod ]
"""


# Accessing the db, or initializing it if it does not exist
# port - default mongodb port is 27017 when initializing on your machine
def init_db(port):
    client = pymongo.MongoClient('localhost', port)
    db = client.pacemakerDB
    return


# adding users to the db upon registration
def insert_user(db, username, password):
    """Insert User Function

    To insert a new user into the database. The new users username and password are required upon creation,
    the users ID should be assigned by the database, and no pacemaker parameters are required upon user creation.

    Args:
        db            : The handler for the initialized database
        username (str): The username of the new user
        password (str): The password of the new user (no hashing is necessary by the database)

    """
    # registering the user
    user = {
        "_id": uuid.uuid4().hex,
        "username": username,
        "password": password,
    }
    # error if 10 users already registered
    cursor = db.users.find({})
    total_users = 0
    for document in cursor:
        total_users += 1
    if(total_users == 10):
        return jsonify({"error": "Maximum number of users already registered"}, 400)
    # storing the user object in the db
    db.users.insert_one(user)


def find_user(db, username=None, password=None):
    """Find User Function

    To find a user in the database. Can be given either a username, or the username and the password. Should return
    a list of all users matching the search query.

    Args:
        db:                                 The handler for the initialized database
        username (str):                     The username of the user
        password (:obj:`str`, optional):    The password of the user (no hashing is necessary by the database)

    Returns:
        (:obj:`list`): A list of all users matching the search query

    """
    if (username is not None and password is not None):
        cursor = db.users.find(
            {{"username": username}, {"password": password}})
    elif (username is not None):
        cursor = db.users.find({"username": username})

    return cursor


def get_user(db, id):
    """Get User By ID

    To get a user by ID from the database. User IDs should be unique as to ensure only one user can ever be 
    returned by this function.

    Args:
        db:     The handler for the initialized database
        id (int):   The unique id of the user

    Returns:
        (:obj:`list`): A single user

    """
    return db.users.find_one({"_id": id})


def get_rows(db):
    """Gets The Number Of Users Stored In The Database

    Args:
        db:     The connection handler for the initialized database

    Returns:
        (int): The number of users in the database

    """
    cursor = db.users.find({})
    for document in cursor:
        total_users += 1

    return total_users


def update_pacemaker_parameters(db, id, values):
    """Update Pacemaker Parameters

    Given a list of pacemaker parameters, whos entries are in the same order as the user list defined in the NOTE,
    updates all the pacemaker parameters for the specified user

    Args:
        db:         The connection handler for the initialized database
        id (int):       The unique id of the user
        (:obj:`list`):  The complete list of pacemaker parameters whos values must be updated in the database

    """
    # mongo integration
    db.users.update({'_id': id}, {
        '$set': {'LowerRateLimit': 0,
                 'UpperRateLimit': 1,
                 'AtrialAmplitude': 2,
                 'AtrialPulseWidth': 3,
                 'AtrialRefractoryPeriod': 4,
                 'VenctricularAmplitude': 5,
                 'VentricularPulseWidth': 6,
                 'VentricularRefractoryPeriod': 7}})
