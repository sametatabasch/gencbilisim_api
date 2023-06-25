import os
import sqlite3

from dotenv import load_dotenv
from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models.Database import Database
from models.Users import Users

app = Flask(__name__)

load_dotenv()  # .env dosyasını yükle
# .env dosyasındaki değişkenleri app.config'e ekle
for key, value in os.environ.items():
    app.config[key] = value

CORS(app)

jwt = JWTManager(app)
db = Database()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'message': 'Geçersiz veri'}), 400

    return Users().login(username, password)



@app.route('/relayStatus', methods=['POST'])
@jwt_required()
def relay_status():
    db.connect()
    relays = None
    try:
        relays = db.cursor.execute("SELECT * FROM relays;").fetchall()
        db.disconnect()
    except sqlite3.Error as e:
        print(e)
        db.disconnect()
    return jsonify(relays)


@app.route('/changeRelayStatus', methods=['POST'])
@jwt_required()
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
        db.connect()
        for relay in relays:
            db.cursor.execute('''UPDATE relays SET status=? WHERE name=?''', (relay['status'], relay['name']))

        db.connection.commit()
        db.disconnect()
        return "Success!"
    except Exception as e:
        db.disconnect()
        return e


@app.route('/get_schedule', methods=['POST'])
@jwt_required()
def get_schedule():
    try:
        #todo hocaya göre ders programı veri tabanından çekilecek
        current_user = get_jwt_identity()
        return jsonify({"schedule": {
            0: {
                "BILP-113": [[10, 0], [15, 0]],
                "BILP-114": [[15, 0], [17, 0]]

            }, 1: {
                "BILP-2": [[12, 0], [20, 29]]
            }, 2: {
                "BILP-3": [[12, 0], [17, 0]]
            }, 3: {
                "GZT-105": [[9, 0], [16, 0]]

            }, 4: {
                "BILP-201": [[8, 0], [10, 00]],
                "BILP-207": [[10, 0], [12, 00]],
                "BILP-107": [[13, 0], [17, 00]],
            },
            5: {

            },
            6: {

            }
        }}), 200
    except Exception as e:
        return jsonify({'message': f'Hata oluştu: {str(e)}'}), 500


@app.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Forbidden",
        "error": str(e),
        "data": None
    }), 403


@app.errorhandler(404)
def forbidden(e):
    return jsonify({
        "message": "Endpoint Not Found",
        "error": str(e),
        "data": None
    }), 404


if __name__ == '__main__':
    app.run()
