from flask import session

from .test_database import find_user, init_db, insert_user, get_rows, update_pacemaker_parameters


class User:

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
        self.config = config
        self.id = ''
        self.username = ''
        self.password = ''

    def create_account(self, username, password):
        conflicts = find_user(username=username)
        num_users = get_rows()
        if conflicts or num_users >= 10:
            return False
        insert_user(username, password)
        self.login(username, password)
        return True

    def login(self, username, password):
        print('function called')
        result = find_user(username=username, password=password)
        print(result)
        print('that was the result')
        if result:
            print(result['id'])
            # self.parameters.update(zip(self.parameters, result[0][3:]))
            # self.id = result.id
            self.id = result['id']
            self.username = result['username']
            self.password = result['password']
            session['logged_in'] = True

    def logout(self):
        self.id = ''
        self.username = ''
        self.password = ''
        self.parameters = dict.fromkeys(self.parameters, None)
        session.pop('logged_in', None)

    def is_loggedin(self):
        return 'logged_in' in session and session['logged_in']

    def get_pacemaker_parameters(self):
        return self.parameters

    def get_username(self):
        return self.username

    def update_pacemaker_parameter(self, key, value):
        if not key in self.parameters:
            return False
        self.parameters[key] = value
        update_pacemaker_parameters(
            self.id, self.parameters.values())

    def update_all_pacemaker_parameters(self, values):
        if len(values) != self.num_parameters:
            return False
        self.parameters.update(zip(self.parameters, values))
        update_pacemaker_parameters(
            self.id, self.parameters.values())
