import sqlite3

from dotenv import load_dotenv
from .Database import Database
from flask import jsonify
from typing import Optional
import os
import traceback

load_dotenv()

db = Database(os.environ.get('ATTENDANCE_DATABASE_PATH'))


class Attendance:
    id = key = date = student_number = lesson_date = lesson_code = ""

    def __init__(self, attendance_id: Optional[int] = None):
        if attendance_id is not None:
            self.id = attendance_id
            self.fill_by_id()
            pass

    def fill_by_id(self):
        if self.id:
            attendances = Attendances()
            attendance = attendances.get_by_id(self.id)
            if attendance:
                self.key = attendance.key
                self.date = attendance.date
                self.student_number = attendance.student_number
                self.lesson_date = attendance.lesson_date
                self.lesson_code = attendance.lesson_code
                return True
        return False

    def fill_by_data(self, data: dict):
        # todo validate data
        if not data or not isinstance(data, dict):
            return jsonify({"error": "(Attendance.fill_by_data) Hatalı veri"}), 500

        required_keys = ['key', 'date', 'student_number', 'lesson_date', 'lesson_code']
        if not all(key in data for key in required_keys):
            return jsonify({"error": "(Attendance.fill_by_data) Eksik veri"}), 500

        self.id = data.get('id')
        self.key = data.get('key')
        self.date = data.get('date')
        self.student_number = data.get('student_number')
        self.lesson_date = data.get('lesson_date')
        self.lesson_code = data.get('lesson_code')
        return True

    def serialize(self):
        return {
            "id": self.id,
            "key": self.key,
            "date": self.date,
            "lesson_date": self.lesson_date,
            "student_number": self.student_number,
            "lesson_code": self.lesson_code
        }


class Attendances:
    table_name = "attendance"

    def __init__(self):
        return

    def create(self, attendance: Attendance):
        if not attendance or not isinstance(attendance, Attendance):
            return jsonify({'error': '(Attendances.create) Yoklama bilgileri yanlış'}), 500

        db.connect()

        try:
            db.cursor.execute(
                f"INSERT INTO {self.table_name} (key, date, student_number, lesson_date, lesson_code) VALUES (?, ?, ?, ?, ?)",
                (attendance.key, attendance.date, attendance.student_number, attendance.lesson_date,
                 attendance.lesson_code)
            )
            db.connection.commit()
            attendance.id = db.cursor.lastrowid
            db.disconnect()
            return jsonify({'message': "Yoklama oluşturuldu", 'attendance': attendance.serialize()})
        except sqlite3.IntegrityError as e:
            return jsonify({'error': f'(Attendances.create) Zaten yoklama alınmış: {str(e)}'}), 429
        except sqlite3.Error as e:
            db.disconnect()
            return jsonify({'error': f'(Attendances.create) Hata oluştu: {str(e)}'}), 500

    def update(self, data: dict):
        if not data or not isinstance(data, dict):
            return jsonify({'error': '(Attendances.update) Hatalı veri'}), 500

        try:
            data_without_id = data.copy()
            data_without_id.pop('id', None)

            update_query = f"UPDATE {self.table_name} SET "
            update_query += ", ".join([f"{column} = ?" for column in data_without_id.keys()])
            update_query += f" WHERE id={data.get('id')}"

            db.connect()
            db.cursor.execute(update_query, list(data_without_id.values()))
            db.connection.commit()
            db.disconnect()
            attendance = Attendance(data.get('id'))
            return jsonify({"message": "Güncelleme başarılı", "attendance": attendance.serialize()})
        except Exception as e:
            tb = traceback.format_exc()  # Hatayı izin (traceback) olarak al
            db.disconnect()
            return jsonify({'error': f'(Attendances.update) Hata oluştu: {str(e)}', 'traceback': tb}), 500

    def get_all(self):
        db.connect()
        db.cursor.execute(f"Select * FROM {self.table_name}")
        students = db.cursor.fetchall()
        # todo dönen değerleri kontrol et
        db.disconnect()
        return students

    def get_by_id(self, attendance_id: int):
        db.connect()
        db.cursor.execute(f"""Select * From {self.table_name} where id=?""", (attendance_id,))
        attendance_data = db.cursor.fetchone()
        if not attendance_data:
            return False
        attendance = Attendance()
        attendance.fill_by_data(attendance_data)
        db.disconnect()
        if not attendance:
            return jsonify({'error': '(Attendances.get_by_id) Yoklama bulunamadı'}), 404
        return attendance

    def delete(self, attendance_id):
        db.connect()
        db.cursor.execute(f"DELETE FROM {self.table_name} WHERE id=?", (attendance_id,))
        db.connection.commit()
        db.disconnect()
        return jsonify({'message': '(Attendances.delete) Yoklama silindi'}), 200
