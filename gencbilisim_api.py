import os
import sqlite3

from dotenv import load_dotenv
from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models.Database import Database
from models.Users import Users
from models.Attendence import Instructors, Instructor, Students, Student
import traceback

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


@app.route("/create_instructor", methods=["POST"])
@jwt_required()
def create_instructor():
    try:
        current_user = get_jwt_identity()

        instructor_data = request.json.get("instructor")
        if instructor_data:
            instructor = Instructor()
            if instructor.fill_by_data(instructor_data):
                instructors = Instructors()
                return instructors.create(instructor)
            else:
                return jsonify({"error": "create_instructor() Hoca bilgileri doldurulamadı"})
        else:
            return jsonify({"error": "create_instructor() Hoca bilgileri eksik"})
    except Exception as e:
        return jsonify({'error': 'create_instructor() Hoca Oluşturulamadı', 'details': str(e)}), 404


@app.route("/update_instructor/<instructor_id>", methods=['PUT'])
@jwt_required()
def update_instructor(instructor_id):
    instructor_data = request.get_json()
    instructor_data['id'] = instructor_id
    instructors = Instructors()
    return instructors.update(instructor_data)


@app.route("/delete_instructor/<instructor_id>", methods=["DELETE"])
@jwt_required()
def delete_instructor(instructor_id):
    instructors = Instructors()
    return instructors.delete(instructor_id)


@app.route('/get_schedule', methods=['POST'])
@jwt_required()
def get_schedule():
    try:
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


@app.route('/get_students', methods=['POST'])
@jwt_required()
def get_students():
    try:
        current_user = get_jwt_identity()
        students = Students().get_all()
        return jsonify({"students": students})
    except Exception as e:
        return jsonify({'error': f'Hata oluştu (get_students): {str(e)}'}), 500


@app.route('/get_student', methods=['POST'])
@jwt_required()
def get_student():
    try:
        current_user = get_jwt_identity()
        student = Students().get_by_card_id(request.json.get('card_id'))
        if isinstance(student, Student):
            return jsonify({"student": student.serialize()})
        else:
            return student
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({'error': f'Hata oluştu (get_students): {str(e)}', 'traceback': tb}), 500


@app.route("/create_student", methods=["POST"])
@jwt_required()
def create_student():
    try:
        current_user = get_jwt_identity()

        student_data = request.json.get("student")
        if student_data:
            student = Student()
            if student.fill_by_data(student_data):
                students = Students()
                return students.create(student)
            else:
                return jsonify({"error": "create_student() Öğrenci bilgileri doldurulamadı"})
        else:
            return jsonify({"error": "create_student() Öğrenci bilgileri eksik"})
    except Exception as e:
        return jsonify({'error': 'create_student() Öğrenci Oluşturulamadı', 'details': str(e)}), 404


@app.route("/update_student/<student_id>", methods=['PUT'])
@jwt_required()
def update_student(student_id):
    student_data = request.get_json()
    student_data['id'] = student_id
    students = Students()
    return students.update(student_data)


@app.route("/delete_student/<student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):
    students = Students()
    return students.delete(student_id)


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
