"""
Database Library
-------------------------
A collection of functions capable of interacting with 
a sqlite3 single file databse. 
NOTE: Users are returned as lists, whose entries are 
in the following order 
        [ _userid, 
        username, 
        password, 
        LowerRateLimit, 
        UpperRateLimit, 
        AtrialAmplitude, 
        AtrialPulseWidth, 
        AtrialRefractoryPeriod, 
        VentricularAmplitude, 
        VentricularPulseWidth, 
        VentricularRefractoryPeriod ]
"""

import sqlite3, os, sys, inspect, datetime, re

thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentfolder = os.path.dirname(thisfolder)
sys.path.insert(0, parentfolder)

from config.config_manager import Config


def init_db(file):
    """init_db Initializes a database located at a given file location

    The file location should be specified relative to the ~/3K04-Pacemaker/DCM/flaskapp/data 
    directory. The file should also have a supported sqlite3 extension (.db .db3 .sdb .s3db 
    .sqlite .sqlite3) and if the file does not already exist it will be created and
    populated with a new databases.

    :param file: The relative file location of the single file sqlite3 database
    :type file: str
    :return: A tuple containing the databases connection handler and cursor (sqlite3.Connection, sqlite3.Cursor)
    :rtype: tuple
    """
    thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    db_file = os.path.join(thisfolder, file)    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(""" --begin-sql
        CREATE TABLE IF NOT EXISTS users (
            _userid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        );
    """)
    conn.commit()
    return conn, cursor


def insert_user(conn, cursor, username, password):
    """insert_user Given a username and password of a new user, will insert the user into the database

    This function will create a new entry in the database of a user with the given username and password. 
    Only the users username and password are initialized upon user creation, the pacemaker parameters will
    default to None, forcing the user to manually enter their parameters.
    NOTE: This function does no check for conflicting users in the database before inserting a new user. 
    It is up to the user of this function to check for conflicts (if they wish to do so) before calling
    this function.

    :param conn: The connection handler for the database to insert a new user into
    :type conn: :class:`sqlite3.Connection`
    :param cursor: The cursor handler for the database to insert a new user into
    :type cursor: :class:`sqlite3.Cursor`
    :param username: The username for the new user
    :type username: str
    :param password: The password for the new user
    :type password: str
    """
    cursor.execute('INSERT INTO users (username, password) VALUES(?,?)', [username, password])
    conn.commit()

    user_id = find_user(cursor, username=username, password=password)[0][0]

    query_string = 'CREATE TABLE IF NOT EXISTS user_{0}( _entryid INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL, mode TEXT'.format(str(user_id))
    parameter_list = [ i.replace(' ', '') for i in Config.getInstance().get('Parameters', 'parameters.values').split(',') ]

    for parameter in parameter_list:
        query_string += ', {0} INTEGER'.format(parameter)

    query_string += ');'

    cursor.execute(query_string)
    conn.commit()

    
def find_user(cursor, username=None, password=None):
    """find_user Given search parameters will find all matching users in the database

    Given one or more of the optional search parameters will return a list of all users
    matching that search criteria. Accepted search parameters are username and password.
    If neither optional parameters are given, the function will return None

    :param cursor: The cursor handler for the database to search for the user in
    :type cursor: :class:`sqlite3.Cursor`
    :param username: The username of the user to search for, defaults to None
    :type username: str, optional
    :param password: The password of the user to search for, defaults to None
    :type password: str, optional
    :return: A list of tuples containing all users matching the search query
    :rtype: list
    """
    if (username is not None and password is not None):
        cursor.execute(""" --begin-sql
            SELECT * FROM users
            WHERE
            (username = '{0}')
            AND
            (password = '{1}');
        """.format(username, password))
    elif (username is not None):
        cursor.execute(""" --begin-sql
            SELECT * FROM users
            WHERE
            (username = '{0}');
        """.format(username))
    elif (password is not None):
        cursor.execute(""" --begin-sql
            SELECT * FROM users
            WHERE
            (password = '{0}');
        """.format(password))
    else:
        return None
    return cursor.fetchall()

def get_user(cursor, id):
    """get_user Returns a complete users information given their unique ID

    Return type is a list of users. Since the search is done by unique ID,
    this list is garunteed to be either of length one, if a user with matching
    unique ID is found, or zero, if no user with matching unique ID is found.

    :param cursor: The cursor handler for the database the user can be found in
    :type cursor: :class:`sqlite3.Cursor`
    :param id: The unique ID of the user to search for
    :type id: int
    :return: A list of tuples containing the contents of the first item matching the search query
    :rtype: list
    """
    cursor.execute(""" --begin-sql
        SELECT * FROM users
        WHERE _userid = {0};
    """.format(str(id)))
    return cursor.fetchall()[0]

def get_user_parameters(cursor, id):
    """get_user_parameters Returns a complete list of the users most recent parameters

    Return type is a list of parameters. Since the search is done by unique ID,
    this list is garunteed to be of constant length, defined by the parameter list
    in the application configuration.

    :param cursor: The cursor handler for the database the user can be found in
    :type cursor: :class:`sqlite3.Cursor`
    :param id: The unique ID of the user to search for
    :type id: int
    :return: A list of the users current pacemaker parameters
    :rtype: list
    """
    cursor.execute(""" --begin-sql
        SELECT * FROM {0};
    """.format('user_' + str(id)))
    result = cursor.fetchall()
    if len(result) > 0:
        return result[0]
    return [-1, 'current', None] + [ None for i in Config.getInstance().get('Parameters', 'parameters.values').split(',') ]

def get_user_history(cursor, id):
    """get_user_history Returns a complete list of all the users past parameters

    Return type is a list of all past parameters, including the current ones. 
    This function has no garunteed list size, as it depends on how many history
    entries the user has made.

    :param cursor: The cursor handler for the database the user can be found in
    :type cursor: :class:`sqlite3.Cursor`
    :param id: The unique ID of the user to search for
    :type id: int
    :return: A list of all the users past pacemaker parameters
    :rtype: list
    """
    cursor.execute(""" --begin-sql
        SELECT * FROM {0};
    """.format('user_' + str(id)))
    result = cursor.fetchall()
    if len(result) > 1:
        return result[1:]
    return []


def get_rows(cursor):
    """get_rows Returns the number of rows (.i.e users) in the database

    :param cursor: The cursor handler for the database
    :type cursor: :class:`sqlite3.Cursor`
    :return: the number of rows contained in the user table of the database
    :rtype: int
    """ 
    cursor.execute(""" --begin-sql
        SELECT COUNT(*) FROM users;
    """)
    return cursor.fetchall()[0][0]

def update_pacemaker_parameters(conn, cursor, id, values):
    """update_pacemaker_parameters Given a list of pacemaker parameters, updates the database values

    When given handler to the database and the unique ID of the user being affected, will update the
    users pacemaker parameters to match the input list.
    NOTE: No complete check is done to ensure the validity of the input, it is up 
    to the method user to ensure the lists correctness.

    :param conn: The connection handler for the database whos contents to change
    :type conn: :class:`sqlite3.Connection`
    :param cursor: The cursor handler for the database whos contents to change
    :type cursor: :class:`sqlite3.Cursor`
    :param id: The unique ID of the user whos parameters should be changed
    :type id: int
    :param values: A list of pacemaker parameters, whos order matches the databases contents
    :type values: list
    """ 
    cursor.execute(""" --begin-sql
        SELECT COUNT(*) FROM {0};
    """.format('user_' + str(id)))
    num_entries = cursor.fetchall()[0][0]

    parameter_list = [ i.replace(' ', '') for i in Config.getInstance().get('Parameters', 'parameters.values').split(',') ]
    
    insert_query = 'SELECT ?, mode'
    create_query = 'INSERT INTO user_{0} (timestamp, mode'.format(id)
    update_query = "UPDATE user_{0} SET mode = '{1}'".format(id, values[0])

    for index, parameter in enumerate(parameter_list, start=1):
        insert_query += ', {0}'.format(parameter)
        create_query += ', {0}'.format(parameter)
        update_query += ", {0} = '{1}'".format(parameter, values[index])
    
    insert_query = create_query + ') ' + insert_query + ' FROM user_{0} WHERE timestamp = ?;'.format(id)
    create_query += ') VALUES(' + '?' + (len(values))*',?' + ');'
    update_query += ' WHERE timestamp = ?;'
    

    if num_entries == 0:
        cursor.execute(create_query, ['current'] + values)
        conn.commit()

    cursor.execute(update_query, ['current'])
    conn.commit()

    timestamp = datetime.datetime.now().strftime(Config.getInstance().get('Database', 'db.timestamp'))

    cursor.execute(insert_query, [timestamp, 'current'])
    conn.commit()