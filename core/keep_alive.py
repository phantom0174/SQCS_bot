from flask import Flask
from threading import Thread
import logging

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.disabled = True


@app.route('/')
def show_panel():
    return 'Bot is alive!'


@app.route('/test')
def hello_world():
    return 'Hello, World'


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()
