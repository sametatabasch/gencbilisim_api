import sqlite3

from dotenv import load_dotenv
from .Database import Database
from flask import jsonify
from typing import Optional
import os
import traceback

load_dotenv()

db = Database(os.environ.get('ATTENDANCE_DATABASE_PATH'))


class Lesson:
    id = name = code = class_hours = ""

    def __init__(self, lesson_code: Optional[str] = None):
        if lesson_code is not None:
            self.code = lesson_code
            self.fill_by_code()
            pass

    def fill_by_id(self):
        if self.id:
            lessons = Lessons()
            lesson = lessons.get_by_id(self.id)
            if lesson:
                self.name = lesson.name
                self.code = lesson.code
                self.class_hours = lesson.class_hours
                return True
        return False

    def fill_by_code(self):
        if self.code:
            lessons = Lessons()
            lesson = lessons.get_by_code(self.code)
            if lesson:
                self.name = lesson.name
                self.code = lesson.code
                self.class_hours = lesson.class_hours
                return True
        return False

    def fill_by_data(self, data: dict):
        # todo validate data
        if not data or not isinstance(data, dict):
            return jsonify({"error": "(Lesson.fill_by_data) Hatalı veri"}), 500

        required_keys = ['name', 'code', 'class_hours']
        if not all(key in data for key in required_keys):
            return jsonify({"error": "(Lesson.fill_by_data) Eksik veri"}), 500

        self.id = data.get('id')
        self.name = data.get('name')
        self.code = data.get('code')
        self.class_hours = data.get('class_hours')
        return True

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "ccode": self.code,
            "class_hours": self.class_hours,
        }


class Lessons:
    table_name = "lessons"

    def __init__(self):
        return

    def create(self, lesson: Lesson):
        if not lesson or not isinstance(lesson, Lesson):
            return jsonify({'error': '(Students.create) Kullanıcı bilgileri yanlış'}), 500

        db.connect()

        try:
            db.cursor.execute(
                f"INSERT INTO {self.table_name} (name, code, class_hours) VALUES (?, ?, ?)",
                (lesson.name, lesson.code, lesson.class_hours)
            )
            db.connection.commit()
            lesson.id = db.cursor.lastrowid
            db.disconnect()
            return jsonify({'message': "Ders oluşturuldu", 'lesson': lesson.serialize()})
        except sqlite3.Error as e:
            db.disconnect()
            return jsonify({'error': f'(Lessons.create) Hata oluştu: {str(e)}'}), 500

    def update(self, data: dict):
        if not data or not isinstance(data, dict):
            return jsonify({'error': '(Lessons.update) Hatalı veri'}), 500

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
            lesson = Lesson(data.get('id'))
            return jsonify({"message": "Güncelleme başarılı", "lesson": lesson.serialize()})
        except Exception as e:
            tb = traceback.format_exc()  # Hatayı izin (traceback) olarak al
            db.disconnect()
            return jsonify({'error': f'(Lessons.update) Hata oluştu: {str(e)}', 'traceback': tb}), 500

    def get_all(self):
        db.connect()
        db.cursor.execute(f"Select * FROM {self.table_name}")
        students = db.cursor.fetchall()
        # todo dönen değerleri kontrol et
        db.disconnect()
        return students

    def get_by_id(self, lesson_id: int):
        db.connect()
        db.cursor.execute(f"""Select * From {self.table_name} where id=?""", (lesson_id,))
        lesson_data = db.cursor.fetchone()
        if not lesson_data:
            return False
        lesson = Lesson()
        lesson.fill_by_data(lesson_data)
        db.disconnect()
        if not lesson:
            return jsonify({'error': '(Lessons.get_by_id) Ders bulunamadı'}), 404
        return lesson

    def get_by_code(self, lesson_code: str):
        db.connect()
        db.cursor.execute(f"""Select * From {self.table_name} where code=?""", (lesson_code,))
        lesson_data = db.cursor.fetchone()
        if not lesson_data:
            return False
        lesson = Lesson()
        lesson.fill_by_data(lesson_data)
        db.disconnect()
        if not lesson:
            return jsonify({'error': '(Lessons.get_by_code) Ders bulunamadı'}), 404
        return lesson

    def delete(self, lesson_id):
        db.connect()
        db.cursor.execute(f"DELETE FROM {self.table_name} WHERE id=?", (lesson_id,))
        db.connection.commit()
        db.disconnect()
        return jsonify({'message': '(Lessons.delete) Ders silindi'}), 200
