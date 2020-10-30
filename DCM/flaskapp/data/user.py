"""
User Class
-------------------------
The class to represent a user of this application. 
Capable of initializing and accessing the database 
specified in the application configuration, as well 
as loggin in and out, creating an account, and 
modifying the pacemaker parameters of the currently 
logged in user.
"""


from flask import session

from .database import find_user, init_db, insert_user, get_rows, update_pacemaker_parameters


class User:
    """This is a class representation of a simple flask app user

    The class to represent a user of this application. 
    Capable of initializing and accessing the database 
    specified in the application configuration, as well 
    as loggin in and out, creating an account, and 
    modifying the pacemaker parameters of the currently 
    logged in user.

    :param config: A handle to the :class:`configparser.ConfigParser` config 
        object initialized by the main application on startup
    :type config: class:`configparser.ConfigParser`
    """
    num_parameters = 8
    parameters = {
        'Lower Rate Limit': None,
        'Upper Rate Limit': None,
        'Atrial Amplitude': None,
        'Atrial Pulse Width': None,
        'Atrial Refractory Period': None,
        'Ventricular Amplitude': None,
        'Ventricular Pulse Width': None,
        'Ventricular Refractory Period': None
    }


    def __init__(self, config):
        """Constructor Method
        """
        self.config = config
        self.id = ''
        self.username = ''
        self.password = ''
        self.conn, self.cursor = init_db(self.config.get('Database', 'db.local-uri'))


    def create_account(self, username, password):
        """create_account Creates a new user account

        Checks the database to ensure no user with the same username exists, 
        and that the maximum allowable local-agents has not been exceeded 
        (defined in the application.ini). If no conflicts exist, a new user 
        is created then both inserted into the database and logged in.

        :param username: The username of the new user being created
        :type username: str
        :param password: The password of the new user being created
        :type password: str
        :return: True if the account creation was successful, False otherwise
        :rtype: bool
        """
        conflicts = find_user(self.cursor, username=username)
        num_users = get_rows(self.cursor)
        if conflicts or num_users[0][0] >= 10:
            return False
        insert_user(self.conn, self.cursor, username, password)
        self.login(username, password)
        return True


    def login(self, username, password):
        """login Attempts to log a user in, given their username and password

        Searches the database to check if the user with matching username and 
        password exists. No conflict management (i.e. ensuring only one user 
        matches that username) is necessary since it is handled on account 
        creation. If a matching user is found the :class:`data.user` is updated 
        with that users information and the user is logged in.

        :param username: The username of the user trying to login
        :type username: str
        :param password: The password of the user trying to login
        :type password: str
        """
        result = find_user(self.cursor, username=username, password=password)        
        if result:
            self.parameters.update(zip(self.parameters, result[0][3:]))
            self.id = result[0][0]
            self.username = result[0][1]
            self.password = result[0][2]
            session['logged_in'] = True


    def logout(self):
        """logout Logs out the currently logged in user
        """
        self.id = ''
        self.username = ''
        self.password = ''
        self.parameters = dict.fromkeys(self.parameters, None)
        session.pop('logged_in', None)


    def is_loggedin(self):
        """is_loggedin Checks if this user is logged in

        :return: True if the user is logged in, False otherwise
        :rtype: bool
        """
        return 'logged_in' in session and session['logged_in']


    def get_pacemaker_parameters(self):
        """get_pacemaker_parameters Returns a dictionary of this users pacemaker parameters

        :return: A dictionary of this users pacemaker parameters
        :rtype: dict
        """
        return self.parameters


    def get_username(self):
        """get_username Returns this users username

        :return: This users username
        :rtype: str
        """
        return self.username


    def update_pacemaker_parameter(self, key, value):
        """update_pacemaker_parameter Updates a single pacemaker parameter

        Given a valid key (one already contained in the pacemaker parameters 
        dictionary), will update the value of that key with the passes in 
        value.

        :param key: A key already contained in the pacemaker parameters dictionary
        :type key: str
        :param value: An updated value for the associated key
        :type value: int
        :return: True if the parameter was sucessfully updated, False otherwise
        :rtype: bool
        """
        if not key in self.parameters:
            return False
        self.parameters[key] = value
        update_pacemaker_parameters(self.conn, self.cursor, self.id, self.parameters.values())
        return True


    def update_all_pacemaker_parameters(self, values):
        """update_all_pacemaker_parameters Updates all pacemaker parameters

        Given a dictionary of pacemaker parameters, in the same order as the values of 
        the pacemaker parameters dictionary, will update every value of the dictionary. 
        NOTE: No complete check is done to ensure the validity of the input, it is up 
        to the method user to ensure the dictionaries correctness.

        :param values: A dictionary of the updated pacemaker parameters
        :type values: dict
        :return: True if the pacemaker parameters were updated sucessfully, False otherwise
        :rtype: bool
        """
        print('VALUES:', values)
        if len(values) != self.num_parameters:
            return False
        self.parameters = values
        print('PARAMETERS:', self.parameters.values())
        update_pacemaker_parameters(self.conn, self.cursor, self.id, self.parameters.values())