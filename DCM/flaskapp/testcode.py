from data.database import update_pacemaker_parameters, init_db

parameters = {
        'Lower Rate Limit': 32,
        'Upper Rate Limit': 1,
        'Atrial Amplitude': None,
        'Atrial Pulse Width': None,
        'Atrial Refractory Period': None,
        'Ventricular Amplitude': None,
        'Ventricular Pulse Width': None,
        'Ventricular Refractory Period': None
    }

init_db('dcm_data.db')