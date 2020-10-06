import configparser, os, logging, datetime

logger = None

def init_config(cfg_files=[]):
    cfg_files.append('application.ini')
    
    thisfolder = os.path.dirname(os.path.abspath(__file__))
    cfg_files[:] = [os.path.join(thisfolder, filename) for filename in cfg_files]

    config = configparser.ConfigParser()
    config.read(cfg_files)

    return config

def init_logging(config):
    global logger
    if logger != None:
        return logger

    thisfolder = os.path.dirname(os.path.abspath(__file__))
    logdir = os.path.join(thisfolder, '../logs/')
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    date = datetime.datetime.now().strftime('%Y-%m-%d-%H.%M.%S')
    name = logdir + 'FLASKAPP-' + date + '.log'

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