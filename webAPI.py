from flask import Flask
from flask import request, jsonify
import sqlite3
import os

app = Flask(__name__)


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




"""
    change factory for novel syntax of json api
"""


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect_sqlite3(db_file=os.path.dirname(__file__) + "/webAPI.db"):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS relays (
                id integer PRIMARY KEY,
                status text DEFAULT "false" NOT NULL,
                name text,
                description text,
                UNIQUE(name)
            );
            """)
        c.execute("""
                INSERT OR IGNORE INTO relays(status,name) VALUES(0, 'relay1'),(0, 'relay2');
            """)
        conn.row_factory = dict_factory
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn


if __name__ == '__main__':
    app.run()
