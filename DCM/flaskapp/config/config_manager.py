"""
Config Manager
-------------------------
A collection of configuration setup
functions, to initialize the config
variables and setup application
logging.
"""


import configparser, os, logging, datetime, inspect

logger = None


def init_config(cfg_files=[]):
    """init_config Initializes the application configuration given a list of configuration files

    Will read all configuration files, creating a application varaible matching the value in the 
    files. File locations in the list must be specified relative to the ~/3K04-Pacemaker/DCM/flaskapp/config 
    directory. The order of the files in the list matters, as any repeat variables will have their previous 
    values overriden. This allows for a default application configuration to be specified and later overriden 
    by an end user.

    :param cfg_files: A list of config file locations, defaults to []
    :type cfg_files: list, optional
    :return: A handler for the applications configuration manager
    :rtype: :class:`configparser.ConfigParser`
    """
    cfg_files.append('application.ini')
    
    thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    cfg_files[:] = [os.path.join(thisfolder, filename) for filename in cfg_files]

    config = configparser.ConfigParser()
    config.read(cfg_files)

    return config


def init_logging(config):
    """init_logging Initializes the application logging

    Will create two logging handlers, a file and stream hendler. This ensures all 
    log output is sent to both the console at runtime as well as a dated log file 
    located in the /logs directory. Both handlers are created as defined in the 
    Logging section of the application configuration files.

    :param config: The handler for the application configuration
    :type config: :class:`configparser.ConfigParser`
    :return: A handler for the applications logging manager
    :rtype: :class:`logging.Logger`
    """
    global logger
    if logger != None:
        return logger

    #thisfolder = os.path.dirname(os.path.abspath(__file__))
    thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    logdir = os.path.join(thisfolder, '../logs/')
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    
    date = datetime.datetime.now().strftime('%Y-%m-%d-%H.%M.%S')
    name = logdir + config.get('Logging', 'logger.file-prefix') + date + '.log'

    logger = logging.getLogger('werkzeug')

    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(name)

    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    c_handler.setFormatter(log_formatter)
    logger.addHandler(c_handler)
    f_handler.setFormatter(log_formatter)
    logger.addHandler(f_handler)

    logger.setLevel(os.environ.get("LOGLEVEL", config.get('Logging', 'logger.level')))

    return logger