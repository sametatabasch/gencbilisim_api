import sqlite3

from dotenv import load_dotenv
from .Database import Database
from flask import jsonify
from typing import Optional
import os
import traceback

load_dotenv()

db = Database(os.environ.get('ATTENDANCE_DATABASE_PATH'))


class Student:
    id = name = last_name = student_number = card_id = lessons = None

    def __init__(self, student_id: Optional[int] = None):
        if student_id is not None:
            self.id = student_id
            self.fill_by_id()
            pass

    def fill_by_id(self):
        if self.id:
            students = Students()
            student = students.get_by_id(self.id)
            if student:
                self.name = student.name
                self.last_name = student.last_name
                self.card_id = student.card_id
                self.student_number = student.student_number
                self.lessons = student.lessons
                return True
        return False

    def fill_by_data(self, data: dict):
        # todo validate data
        if not data or not isinstance(data, dict):
            # todo burada jsonify kullanma
            return jsonify({"error": "(Student.fill_by_data) Hatalı veri"}), 500

        required_keys = ['name', 'last_name', 'card_id', 'student_number', 'lessons']
        if not all(key in data for key in required_keys):
            # todo burada jsonify kullanma
            return jsonify({"error": "(Student.fill_by_data) Eksik veri"}), 500

        self.id = data.get('id')
        self.name = data.get('name')
        self.last_name = data.get('last_name')
        self.card_id = data.get('card_id')
        self.student_number = data.get('student_number')
        self.lessons = data.get('lessons')
        return True

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "card_id": self.card_id,
            "student_number": self.student_number,
            "lessons": self.lessons
        }


class Students:
    table_name = "students"

    def __init__(self):
        return

    def create(self, student: Student):
        if not student or not isinstance(student, Student):
            # todo burada jsonify kullanma
            return jsonify({'error': '(Students.create) Kullanıcı bilgileri yanlış'}), 500

        db.connect()

        try:
            db.cursor.execute(
                f"INSERT INTO {self.table_name} (name, last_name, card_id, student_number) VALUES (?, ?, ?, ?)",
                (student.name, student.last_name, student.card_id, student.student_number)
            )
            db.connection.commit()
            student.id = db.cursor.lastrowid
            db.disconnect()
            # todo burada jsonify kullanma
            return jsonify({'message': "Öğrenci oluşturuldu", 'student': student.serialize()})
        except sqlite3.Error as e:
            db.disconnect()
            # todo burada jsonify kullanma
            return jsonify({'error': f'(Students.create) Hata oluştu: {str(e)}'}), 500

    def update(self, data: dict):
        if not data or not isinstance(data, dict):
            # todo burada jsonify kullanma
            return jsonify({'error': '(Students.update) Hatalı veri'}), 500

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
            student = Student(data.get('id'))
            # todo burada jsonify kullanma
            return jsonify({"message": "Güncelleme başarılı", "student": student.serialize()})
        except Exception as e:
            tb = traceback.format_exc()  # Hatayı izin (traceback) olarak al
            db.disconnect()
            # todo burada jsonify kullanma
            return jsonify({'error': f'(Students.update) Hata oluştu: {str(e)}', 'traceback': tb}), 500

    def get_all(self):
        db.connect()
        db.cursor.execute(f"Select * FROM {self.table_name}")
        students = db.cursor.fetchall()
        # todo dönen değerleri kontrol et
        db.disconnect()
        return students

    def get_by_id(self, student_id: int):
        db.connect()
        db.cursor.execute(f"""Select * From {self.table_name} where id=?""", (student_id,))
        student = db.cursor.fetchone()
        if not student:
            return False
        std = Student()
        std.fill_by_data(student)
        db.disconnect()
        if not std:
            # todo burada jsonify kullanma
            return jsonify({'error': '(Students.get_by_id) Hoca bulunamadı'}), 404
        return std

    def get_by_card_id(self, card_id: str):
        db.connect()
        db.cursor.execute(f"SELECT * FROM {self.table_name} WHERE card_id=?", (card_id,))
        student = db.cursor.fetchone()
        if student:
            std = Student()
            std.fill_by_data(student)
            db.disconnect()
            if not std:
                # todo burada jsonify kullanma
                return jsonify({'error': '(Students.get_by_card_id) Öğrenci Oluşturulamadı'}), 404
        else:
            # todo burada jsonify kullanma
            return jsonify({'error': '(Students.get_by_card_id) Öğrenci bulunamadı'}), 404
        return std

    def get_by_any(self, field: dict):
        if not isinstance(field, dict) or len(field) != 1:
            return jsonify({'error': '(Students.get_by_any) Hatalı veri'}), 400
        field_name, field_value = list(field.items())[0]

        db.connect()
        db.cursor.execute(f"SELECT * FROM {self.table_name} WHERE {field_name}=?", (field_value,))
        student = db.cursor.fetchone()

        if student:
            std = Student()
            std.fill_by_data(student)
            db.disconnect()
            if not std:
                return {'error': '(Students.get_student_by_any) Öğrenci Oluşturulamadı'}
        else:
            return {'error': '(Students.get_student_by_any) Öğrenci bulunamadı'}

        return std

    def delete(self, student_id):
        db.connect()
        db.cursor.execute(f"DELETE FROM {self.table_name} WHERE id=?", (student_id,))
        db.connection.commit()
        db.disconnect()
        #todo burada jsonify kullanma
        return jsonify({'message': '(Students.delete) Öğrenci silindi'}), 200
