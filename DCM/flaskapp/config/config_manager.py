"""
Config Manager
-------------------------
A collection of configuration setup
classes, to initialize the config
variables and setup application
logging as well as allow access to
both the config variables and logging
function directly form anwhere within
the application.
"""

import configparser, os, logging, datetime, inspect

class Config:
    """ The configuration class, holds all the configuration information

    Manages the configuration and provides access to the config through a 
    singleton implementation. Its get method can be called from anywhere
    within the application the Config class is imported.

    :raises Exception: This class is a singleton!
    :raises Exception: Configuration can only be read once!
    :raises Exception: Configutation has not been read, read_config() must be called first!
    """
    __instance = None
    __config_read = None

    @staticmethod
    def getInstance():
        """getInstance Gets the current instance of Config

        If no instance exists, it will create the initial instance
        before returning it.

        :return: A singleton instance of the Config class
        :rtype: :class:`config_manager.Config`
        """
        if Config.__instance == None:
            Config()
        return Config.__instance

    def __init__(self):
        """__init__ Constructor for the singleton class

        Will raise an exception if called anywhere from outside its own class

        :raises Exception: This class is a singleton!
        """
        if Config.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Config.__instance = self

    def read_config(self, cfg_files=[]):
        """read_config Reads the configuration files

        Called on instance initialization. Will search the config
        directory for all .ini files and read their variable values
        into the Config Manager. Raises an exception if called more
        than once, to ensure variables are not changed mid execution.

        :param cfg_files: A list of additional ini files to read, application.ini is added automatically, defaults to []
        :type cfg_files: list, optional
        :raises Exception: Configuration can only be read once!
        """
        if Config.__config_read != None:
            raise Exception("Configuration can only be read once!")
        else:
            if type(cfg_files) == str:
                cfg_files = [cfg_files]
            if 'application.ini' in cfg_files:
                cfg_files.remove('application.ini')
            cfg_files.insert(0, 'application.ini')

            
            thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            cfg_files[:] = [os.path.join(thisfolder, filename) for filename in cfg_files]

            config = configparser.ConfigParser()
            config.read(cfg_files)

            self.__config = config

            Config.__config_read = True

    def reset_config(self):
        Config.__config_read = None

    def is_config_read(self):
        return Config.__config_read != None

    def get(self, section, variable):
        """get Gets a variable from the configuration

        Given a configuration section and variable name within that section
        will return the value of the variable as a string

        :param section: The section in the configuration file to find the variable in
        :type section: str
        :param variable: The variable name to read from the section
        :type variable: str
        :raises Exception: Configutation has not been read, read_config() must be called first!
        :return: The string representation of the variable
        :rtype: str
        """
        if Config.__config_read == None:
            raise Exception("Configutation has not been read, read_config() must be called first!")
        else:
            return self.__config.get(section, variable)

    def getboolean(self, section, variable):
        """getboolean Gets a variable from the configuration

        Given a configuration section and variable name within that section
        will return the value of the variable as a boolean. The value in the
        configuration file can only be in the form [yes/no, true/false, on/off, 1/0],
        for any other values this method will throw an error

        :param section: The section of the configuration file to find the variable in
        :type section: str
        :param variable: The variable to read form the section
        :type variable: str
        :raises Exception: Configuration has not been rean, read_config() must be called first!
        :return: The boolean representation of the variable
        :rtype: bool
        """
        if Config.__config_read == None:
            raise Exception("Configuration has not been rean, read_config() must be called first!")
        else:
            return self.__config.getboolean(section, variable)

    def get_all(self, section):
        """get_all Gets all variable and values within a section

        Given a configuration section from the configuration files
        will return a dictionary containing all variable names and
        values from within that section. All varaible names and values
        are stored in their string representation within the dictionary.

        :param section: The section of the configuration file to read
        :type section: str
        :raises Exception: Configutation has not been read, read_config() must be called first!
        :return: A dictionary conatianing variable name, value pairs
        :rtype: dict
        """
        if Config.__config_read == None:
            raise Exception("Configutation has not been read, read_config() must be called first!")
        else:
            return self.__config.items(section)



class Logger:
    """ The Logger class, holds all logging information

    This class can initialize a logger through a singleton
    implementation. Its method can be called from anywhere 
    within the application where the Logger class is imported.

    :raises Exception: This class is a singleton!
    :raises Exception: Logger can only be started once!
    """
    __instance = None
    __logger_started = None
    
    @staticmethod
    def getInstance():
        """getInstance Get the current instance of Logger

        If no instance exists it will create the initial
        instance before returning it

        :return: A singleton instance of the Logger class
        :rtype: :class:`config_manager.Logger`
        """
        if Logger.__instance == None:
            Logger()
        return Logger.__instance

    def __init__(self):
        """__init__ Constructor for the singleton class

        Will raise an exception if called anyewhere from outside its own class.

        :raises Exception: This class is a singleton!
        """
        if Logger.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Logger.__instance = self

    def start_logger(self, config):
        """start_logger Starts the logger

        This method must be called by the main block of the application.
        It will create the log file and start the logging process both to
        the log file and the terminal

        :param config: The Instance of Config, which must be created and initialized before the Logger is started
        :type config: :class:`config_manager.Config`
        :raises Exception: Logger can only be started once!
        """
        if Logger.__logger_started != None:
            raise Exception("Logger can only be started once!")
        else:
            thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            logdir = os.path.join(thisfolder, '../logs/')
            if not os.path.exists(logdir):
                os.makedirs(logdir)
            
            date = datetime.datetime.now().strftime(Config.getInstance().get('Logging', 'logger.date-format'))
            name = logdir + config.get('Logging', 'logger.file-prefix') + date + '.log'

            logger = logging.getLogger('werkzeug')

            c_handler = logging.StreamHandler()
            f_handler = logging.FileHandler(name)

            log_formatter = logging.Formatter(Config.getInstance().get('Logging', 'logger.log-format'))

            c_handler.setFormatter(log_formatter)
            logger.addHandler(c_handler)
            f_handler.setFormatter(log_formatter)
            logger.addHandler(f_handler)

            logger.setLevel(os.environ.get("LOGLEVEL", config.get('Logging', 'logger.level')))

            self.__logger = logger

            Logger.__logger_started = True


    def reset_logger(self):
        Logger.__logger_started = None

    def is_logger_started(self):
        return Logger.__logger_started != None

        
    def log(self, level, msg):
        """log Will log a message

        Given a message and the level of that message, this
        method will log the message to all the Loggers handlers
        (i.e. file and terminal) only if the log level is equal
        to or higher than the Logger's log level defined in the
        applications configuration.

        :param level: The level of the message being logged can take the values: DEBUG, INFO, WARN, ERROR, CRITICAL
        :type level: str
        :param msg: The message to be logged by the Logger
        :type msg: str
        """
        level = str.upper(level)

        if level == 'DEBUG':
            self.__logger.debug(msg)
        elif level == 'INFO':
            self.__logger.info(msg)
        elif level == 'WARN':
            self.__logger.warn(msg)
        elif level == 'ERROR':
            self.__logger.error(msg)
        elif level == 'CRITICAL':
            self.__logger.critical(msg)