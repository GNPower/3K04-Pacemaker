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


import os, inspect, sys, re, json, csv, tempfile
from flask import session
from datetime import date

thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentfolder = os.path.dirname(thisfolder)
sys.path.insert(0, parentfolder)

from data.database import init_db, insert_user, get_rows, find_user, get_user, get_user_parameters, get_user_history, update_pacemaker_parameters
from config.config_manager import Config


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


    def __init__(self):
        """Constructor Method
        """
        self.__parameters = { i.replace(' ', '') : None for i in Config.getInstance().get('Parameters', 'parameters.values').split(',') }
        self.__num_parameters = len(self.__parameters)
        self.__mode = None
        self.__id = ''
        self.__username = ''
        self.__password = ''
        self.__conn, self.__cursor = init_db(Config.getInstance().get('Database', 'db.local-uri'))
        self.__set_limits()


    def __set_limits(self):
        """__set_limits Sets the limits of user parameters

        A private function called by the contructor upon user creation.
        Will search the application configuration and implement any
        parameter limits defined there. Limits are enforced in the entry
        form on the DCM, not the database to ensure a more robust DCM.
        """
        raw_limits = dict(Config.getInstance().get_all('Limits'))
        limits = {}
        for key in self.__parameters.keys():
            query = 'limits.' + re.sub(r"(\w)([A-Z])", r"\1 \2", key).lower()
            disable_query = re.sub(r"(\w)([.])", r"\1.can-disable\2", query)
            limit_entry = {}
            should_add_entry = False
            if query in raw_limits.keys():
                limit_entry['min'] = float(raw_limits[query].split(',')[0])
                limit_entry['max'] = float(raw_limits[query].split(',')[1])
                limit_entry['inc'] = float(raw_limits[query].split(',')[2])
                should_add_entry = True
            if disable_query in raw_limits.keys():
                limit_entry['can_disable'] = bool(raw_limits[disable_query])
                should_add_entry = True
            if should_add_entry:
                limits[re.sub(r"(\w)([A-Z])", r"\1 \2", key)] = limit_entry
        self.__limits = limits


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
        if find_user(self.__cursor, username=username) or get_rows(self.__cursor) >= 10:
            return False
        insert_user(self.__conn, self.__cursor, username, password)
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
        result = find_user(self.__cursor, username=username, password=password)     
        if result:
            self.__id = result[0][0]
            self.__username = result[0][1]
            self.__password = result[0][2]
            param_values = get_user_parameters(self.__cursor, self.__id)
            self.__mode = param_values[2]
            self.__parameters.update(zip(self.__parameters, param_values[3:]))
            session['logged_in'] = True


    def logout(self):
        """logout Logs out the currently logged in user
        """
        self.__id = ''
        self.__username = ''
        self.__password = ''
        self.__mode = None
        self.__parameters = dict.fromkeys(self.__parameters, None)
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
        return self.__parameters

    def get_pacemaker_mode(self):
        """get_pacemaker_mode Returns the current pacemaker mode

        :return: The current pacemaker mode, can be either a String or None
        :rtype: str
        """
        return self.__mode

    def get_history(self):
        """get_history Get the users history

        Gets the users curretn history by calling the database
        helper function

        :return: A list fo the users history, including the current pacemaker values
        :rtype: list
        """
        return get_user_history(self.__cursor, self.__id)

    def create_history_file(self):
        """create_history_file Creates a csv file containing the users parameter history
        """
        history = self.get_history()
        data_file = open(os.path.join(parentfolder, 'downloads', str(self.__username) + '-User-History-' + str(date.today()) + '.csv' ), 'w')
        csv_writer = csv.writer(data_file)
        test_headers = ['Date', 'Mode'] + Config.getInstance().get('Parameters', 'parameters.values').split(',')
        csv_writer.writerow(test_headers)
        for entry in history:
            csv_writer.writerow(entry[1:])
        data_file.close()

    def get_limits(self):
        """get_limits Get the users parameter limits

        Returns a dictionary of all the users parameter limits
        as they were defined in the application configuration

        :return: A dictionary of the users parameter limits
        :rtype: dict
        """
        return self.__limits

    def get_username(self):
        """get_username Returns this users username

        :return: This users username
        :rtype: str
        """
        return self.__username

    def get_db_handlers(self):
        return self.__conn, self.__cursor

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
        if not key in self.__parameters:
            return False
        self.__parameters[key] = value
        update_pacemaker_parameters(self.__conn, self.__cursor, self.__id, [self.__mode] + list(self.__parameters.values()))
        return True

    def update_pacemaker_mode(self, mode):
        """update_pacemaker_mode Changes the pacemaker mode

        Given a mode that is contained in the application
        configurations list of allowed modes, will change 
        the current pacemaker mode to the new one. If no 
        valid mode is given will do nothing and return
        False.

        :param mode: The pacemaker mode to change to
        :type mode: str
        :return: True if the pacemaker mode was successfully changed, Fale otherwise
        :rtype: bool
        """
        allowed_modes = Config.getInstance().get('Parameters', 'parameters.modes').split(',')
        if not mode in allowed_modes:
            return False
        self.__mode = mode
        update_pacemaker_parameters(self.__conn, self.__cursor, self.__id, [self.__mode] + list(self.__parameters.values()))
        return True


    def update_all_pacemaker_parameters(self, values):
        """update_all_pacemaker_parameters Updates all pacemaker parameters

        Given a list of pacemaker parameters, in the same order as the values of 
        the pacemaker parameters dictionary, will update every value of the dictionary. 
        NOTE: No complete check is done to ensure the validity of the input, it is up 
        to the method user to ensure the lists correctness.

        :param values: An ordered list of the updated pacemaker parameters
        :type values: list
        :return: True if the pacemaker parameters were updated sucessfully, False otherwise
        :rtype: bool
        """
        if len(values) != self.__num_parameters:
            return False
        self.__parameters.update(zip(self.__parameters, values))
        update_pacemaker_parameters(self.__conn, self.__cursor, self.__id, [self.__mode] + list(self.__parameters.values()))
        return True