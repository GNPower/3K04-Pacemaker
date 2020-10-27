import sqlite3, os, inspect

"""
NOTE:   Users are expected to be returned as lists, whose entries are in the following order
        [ _userid, username, password, LowerRateLimit, UpperRateLimit, AtrialAmplitude, AtrialPulseWidth, AtrialRefractoryPeriod, VentricularAmplitude, VentricularPulseWidth, VentricularRefractoryPeriod ]
"""


def init_db(file):
    """Database Initialization Function
    To be called on app startup, should load the database at the file location specified, 
    or create it if one doesn't already exist.
    Args:
    
        file (str): The file location of the database, given relative to the ~/PacemakerProject/DCM/flaskapp/data directory
    Returns:
        conn, cursor: The connection handlers for the initialized database
    """
    thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    db_file = os.path.join(thisfolder, file)    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(""" --begin-sql
        CREATE TABLE IF NOT EXISTS users (
            _userid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            LowerRateLimit INTEGER,
            UpperRateLimit INTEGER,
            AtrialAmplitude INTEGER,
            AtrialPulseWidth INTEGER,
            AtrialRefractoryPeriod INTEGER,
            VentricularAmplitude INTEGER,
            VentricularPulseWidth INTEGER,
            VentricularRefractoryPeriod INTEGER
        );
    """)
    conn.commit()
    return conn, cursor


def insert_user(conn, cursor, username, password):
    """Insert User Function
    To insert a new user into the database. The new users username and password are required upon creation, 
    the users ID should be assigned by the database, and no pacemaker parameters are required upon user creation.
    Args:
        conn, cursor:   The connection handlers for the initialized database
        username (str): The username of the new user
        password (str): The password of the new user (no hashing is necessary by the database)
    """
    cursor.execute('INSERT INTO users (username, password) VALUES(?,?)', [username, password])
    conn.commit()
    


def find_user(cursor, username=None, password=None):
    """Find User Function
    To find a user in the database. Can be given either a username, password, or both. Should return
    a list of all users matching the search query.
    Args:
        cursor:                             The connection handler for the initialized database
        username (str):                     The username of the user
        password (:obj:`str`, optional):    The password of the user (no hashing is necessary by the database)
    Returns:
        (:obj:`list`): A list of all users matching the search query
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
    return cursor.fetchall()    

def get_user(cursor, id):
    """Get User By ID
    To get a user by ID from the database. User IDs should be unique as to ensure only one user can ever be 
    returned by this function.
    Args:
        cursor:     The connection handler for the initialized database
        id (int):   The unique id of the user
    Returns:
        (:obj:`list`): A single user
    """
    cursor.execute(""" --begin-sql
            SELECT * FROM users
            WHERE
            (_userid = '{0}');
        """.format(id))
    return cursor.fetchall()

def get_rows(cursor):
    """Gets The Number Of Users Stored In The Database
    Args:
        cursor:     The connection handler for the initialized database
    Returns:
        (int): The number of users in the database
    """
    cursor.execute(""" --begin-sql
        SELECT COUNT(*) FROM users;
    """)
    return cursor.fetchall()

def update_pacemaker_parameters(conn, cursor, id, values):
    """Update Pacemaker Parameters
    Given a list of pacemaker parameters, whos entries are in the same order as the user list defined in the NOTE,
    updates all the pacemaker parameters for the specified user
    Args:
        cursor:         The connection handler for the initialized database
        id (int):       The unique id of the user
        (:obj:`list`):  The complete list of pacemaker parameters whos values must be updated in the database
    """
    cursor.execute(""" --begin-sql
        UPDATE users
        SET
        LowerRateLimit = '{0}',
        UpperRateLimit = '{1}',
        AtrialAmplitude = '{2}',
        AtrialPulseWidth = '{3}',
        AtrialRefractoryPeriod = '{4}',
        VentricularAmplitude = '{5}',
        VentricularPulseWidth = '{6}',
        VentricularRefractoryPeriod = '{7}'
        WHERE
        _userid = {8};
    """.format(*values, id))
    conn.commit()