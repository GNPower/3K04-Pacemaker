from flask import Flask, render_template
from threading import Timer
from config.config_manager import init_logging, init_config
import webbrowser


config = init_config()
logger = init_logging(config)
logger.info('testing...')
app = Flask(__name__)


@app.route("/")
def home():
    logger.debug("this is a debug log")
    return render_template("home.html")

def open_browser():
    webbrowser.open_new('http://' + config.get('HostSelection','host.address') + ':' + config.get('HostSelection', 'host.port') + "/")
    pass

if __name__ == '__main__':
    Timer(1, open_browser).start()
    #WARNING: Change 'use_reloader' to False before shipping release
    app.run(debug=False, host=config.get('HostSelection', 'host.address'), port=config.get('HostSelection', 'host.port'), use_reloader=False)