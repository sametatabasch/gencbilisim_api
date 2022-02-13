from flask import Flask
from flask import request, jsonify
from Data import data
import sqlite3

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/relayStatus')
def role_status():
    db = connect_sqlite3()
    c= db.cursor()
    try:
        relays = c.execute("SELECT * FROM relays;").fetchall()
        print(data)
        print(relays)
    except sqlite3.Error as e:
        print(e)
    return jsonify(relays)


@app.route('/changeRelayStatus')
def change_relay_status():
    return request.args
"""
    change factory for novel syntax of json api
"""
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def connect_sqlite3(db_file="webAPI.db"):
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
                INSERT OR IGNORE INTO relays(status,name) VALUES('false', 'relay1'),('false', 'relay2');
            """)
        conn.row_factory = dict_factory
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn


if __name__ == '__main__':
    app.run()
