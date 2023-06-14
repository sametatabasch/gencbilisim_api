from flask import Flask
from flask import request, jsonify
import sqlite3
import os
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()  # .env dosyasını yükle
# .env dosyasındaki değişkenleri app.config'e ekle
for key, value in os.environ.items():
    app.config[key] = value

CORS(app)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/relayStatus')
def role_status():
    db = connect_sqlite3()
    c = db.cursor()
    relays = None
    try:
        relays = c.execute("SELECT * FROM relays;").fetchall()
    except sqlite3.Error as e:
        print(e)
    return jsonify(relays)


@app.route('/changeRelayStatus')
def change_relay_status():
    args = request.args
    relays = [
        {
            'name': 'relay1',
            'status': args['relay1'],
        },
        {
            'name': 'relay2',
            'status': args['relay2'],
        }
    ]
    try:
        db = connect_sqlite3()
        c = db.cursor()
        for relay in relays:
            c.execute('''UPDATE relays SET status=? WHERE name=?''', (relay['status'], relay['name']))

        db.commit()
        return "Success!"
    except Exception as e:
        return e


def dict_factory(cursor, row):
    """
        change factory for novel syntax of json api
        database data return dict instead of tuple
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect_sqlite3(db_file=app.config['DATABASE_PATH']):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        conn.row_factory = dict_factory
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn


if __name__ == '__main__':
    app.run()
