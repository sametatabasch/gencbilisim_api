import json
import sqlite3

from dotenv import load_dotenv
from .Database import Database
from flask import jsonify
from typing import Optional
import os
import traceback

load_dotenv()

db = Database(os.environ.get('ATTENDANCE_DATABASE_PATH'))


class Instructor:
    id = name = last_name = card_id = schedule = None

    def __init__(self, instructor_id: Optional[int] = None):
        if instructor_id is not None:
            self.id = instructor_id
            self.fill_by_id()
            pass

    def fill_by_id(self):
        if self.id:
            instructors = Instructors()
            instructor = instructors.get_by_id(self.id)
            if instructor:
                self.name = instructor.name
                self.last_name = instructor.last_name
                self.card_id = instructor.card_id
                self.schedule = instructor.schedule
                return True
        return False

    def fill_by_data(self, data: dict):
        # todo validate data
        if not data or not isinstance(data, dict):
            return jsonify({"error": "(Instructor.fill_by_data) Hatalı veri"}), 500

        required_keys = ['name', 'last_name', 'card_id', 'schedule']
        if not all(key in data for key in required_keys):
            return jsonify({"error": "(Instructor.fill_by_data) Eksik veri"}), 500

        self.id = data.get('id')
        self.name = data.get('name')
        self.last_name = data.get('last_name')
        self.card_id = data.get('card_id')
        self.schedule = data.get('schedule')
        return True

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "card_id": self.card_id,
            "schedule": self.schedule,
        }


class Instructors:
    table_name = "instructors"

    def __init__(self):
        return

    def create(self, instructor: Instructor):
        if not instructor or not isinstance(instructor, Instructor):
            return jsonify({'error': '(Instructors.create) Kullanıcı bilgileri yanlış'}), 500

        db.connect()

        try:
            db.cursor.execute(
                f"INSERT INTO {self.table_name} (name, last_name, card_id, schedule) VALUES (?, ?, ?, ?)",
                (instructor.name, instructor.last_name, instructor.card_id, json.dumps(instructor.schedule))
            )
            db.connection.commit()
            instructor.id = db.cursor.lastrowid
            db.disconnect()
            return jsonify({'message': "Hoca oluşturuldu", 'instructor': instructor.serialize()})
        except sqlite3.Error as e:
            db.disconnect()
            return jsonify({'error': f'(Instructors.create) Hata oluştu: {str(e)}'}), 500

    def update(self, data: dict):
        if not data or not isinstance(data, dict):
            return jsonify({'error': '(Instructors.update) Hatalı veri'}), 500

        try:
            data_without_id = data.copy()
            data_without_id.pop('id', None)
            if data_without_id.get('schedule'):
                data_without_id['schedule'] = json.dumps(data_without_id['schedule'])

            update_query = f"UPDATE {self.table_name} SET "
            update_query += ", ".join([f"{column} = ?" for column in data_without_id.keys()])
            update_query += f" WHERE id={data.get('id')}"

            db.connect()
            db.cursor.execute(update_query, list(data_without_id.values()))
            db.connection.commit()
            db.disconnect()
            instructor = Instructor(data.get('id'))
            return jsonify({"message": "Güncelleme başarılı", "instructor": instructor.serialize()})
        except Exception as e:
            tb = traceback.format_exc()  # Hatayı izin (traceback) olarak al
            db.disconnect()
            return jsonify({'error': f'(Instructors.update) Hata oluştu: {str(e)}', 'traceback': tb}), 500

    def get_all(self):
        db.connect()
        db.cursor.execute(f"Select * FROM {self.table_name}")
        instructors = db.cursor.fetchall()
        # todo dönen değerleri kontrol et
        db.disconnect()
        return instructors

    def get_by_id(self, instructor_id: int):
        db.connect()
        db.cursor.execute(f"""Select * From {self.table_name} where id=?""", (instructor_id,))
        instructor = db.cursor.fetchone()
        if not instructor:
            return False
        i = Instructor()
        i.fill_by_data(instructor)
        db.disconnect()
        if not i:
            return jsonify({'error': '(Instructors.get_by_id) Hoca bulunamadı'}), 404
        return i

    def get_by_card_id(self, card_id: str):
        db.connect()
        db.cursor.execute(f"SELECT * FROM {self.table_name} WHERE card_id=?", (card_id,))
        instructor = db.cursor.fetchone()
        if not instructor:
            return False
        i = Instructor()
        i.fill_by_data(instructor)
        db.disconnect()
        if not i:
            return jsonify({'error': '(Instructors.get_card_id)Hoca bulunamadı'}), 404
        return i

    def delete(self, instructor_id):
        db.connect()
        db.cursor.execute(f"DELETE FROM {self.table_name} WHERE id=?", (instructor_id,))
        db.connection.commit()
        db.disconnect()
        return jsonify({'message': '(Instructors.delete) Hoca silindi'}), 200


class Students:
    table_name = "students"

    def __init__(self):
        return

    def create(self):
        pass

    def get_all(self):
        db.connect()
        db.cursor.execute(f"Select * FROM {self.table_name}")
        students = db.cursor.fetchall()
        # todo dönen değerleri kontrol et
        db.disconnect()
        return students

    def get_bay_id(self, std_id: int):
        pass

    def get_by_card_id(self, card_id: str):
        pass

    def delete(self, std_id: int):
        pass
