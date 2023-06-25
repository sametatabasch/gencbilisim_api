"""User Model"""
import sqlite3

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from .Database import Database
from flask import jsonify
from flask_jwt_extended import create_access_token

load_dotenv()

db = Database()


class User:
    id = name = email = username = password = active = ""

    def __init__(self, user_id=None):
        if user_id:
            self.id = user_id
            self.fill_by_id()
        return

    def fill_by_id(self):
        user = Users.get_by_id(self.id)
        self.name = user.name
        self.email = user.email
        self.username = user.username
        self.password = user.password
        self.active = user.active

    def fill_by_data(self, data):
        """

        :param data: dict
        :return:
        """
        if not data or not isinstance(data, dict):
            return False

        required_keys = ['id', 'name', 'email', 'username', 'password', 'active']
        if not all(key in data for key in required_keys):
            return False

        self.id = data['id']
        self.name = data['name']
        self.email = data['email']
        self.username = data['username']
        self.password = data['password']
        self.active = data['active']
        return True

    def serialize(self):
        return \
            {
                "id": self.id,
                "name": self.name,
                "email": self.email,
                "username": self.username,
                "password": self.password,
                "active": self.active
            }


class Users:
    def __init__(self):
        return

    def create(self, data):
        """

        :param data: dict
        :return:
        """

        if data or not isinstance(data, dict):
            return False
        db.connect()
        try:
            db.cursor.execute(
                "INSERT INTO users (name, email, username, password, active) VALUES (?, ?, ?, ?, ?)",
                (data['name'], data['email'], data['username'], generate_password_hash(data['password']), True)
            )
            db.connection.commit()
            user_id = db.cursor.lastrowid
        except sqlite3.Error as e:
            db.disconnect()
            return jsonify({'error': f'Hata oluştu: {str(e)}'}), 500
        return User(user_id)

    def get_all(self):
        db.connect()
        db.cursor.execute("SELECT * FROM users WHERE active=1")
        users = db.cursor.fetchall()
        # todo dönen değeri kontrol et
        db.disconnect()
        return users

    def get_by_id(self, user_id):
        """

        :param user_id:
        :return: User
        """
        db.connect()
        db.cursor.execute("SELECT * FROM users WHERE id=? AND active=1", (user_id,))
        user = db.cursor.fetchone()
        u = User()
        u.fill_by_data(user)
        db.disconnect()
        if not u:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        return u

    def get_by_username(self, username):
        """

        :param username:
        :return: User
        """
        db.connect()
        db.cursor.execute("SELECT * FROM users WHERE username=? AND active=1", (username,))
        user = db.cursor.fetchone()
        u = User()
        u.fill_by_data(user)
        if not u:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        return u

    def update(self, data):
        """

        :param data:
        :return:
        """
        if not data or not isinstance(data, dict):
            return False
        old_user = User(data['id'])
        new_user = User()
        new_user.fill_by_data(data)

        if old_user == new_user:
            print("Kullanıcılar aynı")
        else:
            print("Kullanıcılar farklı")

        """  db.connect()
        db.cursor.execute(
            "UPDATE users SET name=? WHERE id=?",
            (data.get("name"), user_id)
        )
        conn.commit()
        return self.get_by_id(user_id)"""

    def delete(self, user_id):
        db.connect()
        db.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        db.connection.commit()
        db.disconnect()
        return True

    def disable_account(self, user_id):
        db.connect()
        db.cursor.execute(
            "UPDATE users SET active=0 WHERE id=?",
            (user_id,)
        )
        db.connection.commit()
        db.disconnect()
        return self.get_by_id(user_id)

    def login(self, username, password):
        user = self.get_by_username(username)

        if not user or not check_password_hash(user.password, password):
            return jsonify({'error': 'Geçersiz kullanıcı adı veya şifre'}), 401

        try:
            access_token = create_access_token(identity=user.serialize())
            return jsonify({'access_token': access_token}), 200
        except Exception as e:
            return jsonify({'error': f'Hata oluştu: {str(e)}'}), 500
