from flask import Flask
from threading import Thread


app = Flask(__name__)


@app.route('/')
def home():
    return "Use the second link if the first link gives an IndexError. This keep_alive.py is made to keep the repl alive if you are hosting thing using repl"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
