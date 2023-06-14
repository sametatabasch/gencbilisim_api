import os
import sqlite3

from dotenv import load_dotenv
from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from .models.Database import Database

app = Flask(__name__)

load_dotenv()  # .env dosyasını yükle
# .env dosyasındaki değişkenleri app.config'e ekle
for key, value in os.environ.items():
    app.config[key] = value

CORS(app)

jwt = JWTManager(app)
db = Database()


# Kullanıcı verilerini veritabanından sorgulama
def get_user(username):
    db.connect()
    db.cursor.execute('SELECT * FROM users WHERE username = ? AND active = ?', (username, 1,))
    return db.cursor.fetchone()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'message': 'Geçersiz kullanıcı adı veya şifre'}), 400

    user = get_user(username)

    if not user or user['password'] != password:
        return jsonify({'message': 'Geçersiz kullanıcı adı veya şifre'}), 401

    try:
        access_token = create_access_token(identity=user)
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return jsonify({'message': f'Hata oluştu: {str(e)}'}), 500


# Korumalı bir rotaya örnek
@app.route('/protected', methods=['POST'])
@jwt_required()
def protected():
    try:
        current_user = get_jwt_identity()
        return jsonify({'message': f'Hoş geldin, {current_user["name"]}! Bu korumalı veriye erişebilirsin.'}), 200
    except Exception as e:
        return jsonify({'message': f'Hata oluştu: {str(e)}'}), 500


@app.route('/relayStatus')
def role_status():
    db.connect()
    relays = None
    try:
        relays = Database.cursor.execute("SELECT * FROM relays;").fetchall()
        db.disconnect()
    except sqlite3.Error as e:
        print(e)
        db.disconnect()
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
        db.connect()
        for relay in relays:
            db.cursor.execute('''UPDATE relays SET status=? WHERE name=?''', (relay['status'], relay['name']))

        db.connection.commit()
        db.disconnect()
        return "Success!"
    except Exception as e:
        db.disconnect()
        return e


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
