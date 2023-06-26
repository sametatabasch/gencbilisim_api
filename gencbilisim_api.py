import os
import sqlite3

from dotenv import load_dotenv
from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models.Database import Database
from models.Users import Users
from models.Instructors import Instructor, Instructors

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
        return jsonify({'error': '(login) Geçersiz veri'}), 400

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
        # todo hocaya göre ders programı veri tabanından çekilecek
        current_user = get_jwt_identity()
        instructor = Instructors().get_by_card_id(request.json.get('card_id'))
        if not instructor:
            return jsonify(
                {'error': 'Hoca Bulunamadı'}), 404
        else:
            return jsonify(
                {"schedule": instructor.schedule, "name": instructor.name, "last_name": instructor.last_name}), 200
    except Exception as e:
        return jsonify({'error': f'Hata oluştu (get schedule): {str(e)}'}), 500


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
