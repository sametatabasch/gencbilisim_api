from dotenv import load_dotenv
import sqlite3
import os
import secrets
import json
from werkzeug.security import generate_password_hash

load_dotenv(".env")

DATABASE_PATH = os.environ.get('DATABASE_PATH')
ATTENDANCE_DATABASE_PATH = os.environ.get('ATTENDANCE_DATABASE_PATH')
ROOT_PATH = os.environ.get('ROOT_PATH')


def create_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            active INTEGER DEFAULT 1
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relays (
            id integer PRIMARY KEY,
            status text DEFAULT "false" NOT NULL,
            name text,
            description text,
            UNIQUE(name)
        );
    ''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect(ATTENDANCE_DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            last_name TEXT,
            student_number TEXT,
            card_id TEXT,
            lessons TEXT,
            UNIQUE(student_number),
            UNIQUE(card_id)
    );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instructors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            last_name TEXT,
            card_id TEXT,
            schedule TEXT,
            UNIQUE(card_id)
        );
        ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                code TEXT,
                class_hours TEXT,
                UNIQUE(code)
            );
            ''')
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT,
                    date TEXT,
                    student_number TEXT,
                    lesson_date TEXT,
                    lesson_code TEXT,
                    UNIQUE(key)
                );
                ''')
    conn.commit()
    conn.close()
    print("Veri tabanı tabloları oluşturuldu")


def insert_initial_data():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Kullanıcı ekleme
    cursor.execute('''
        INSERT OR IGNORE INTO users (name, username, email, password, active)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Samet ATABAŞ', 'sametatabasch', 'sametatabasch@gmail.com', generate_password_hash('P@swd123'), 1))
    # Add Relays
    cursor.execute('''INSERT OR IGNORE INTO relays(status,name) VALUES(0, 'relay1'),(0, 'relay2');
    ''')

    conn.commit()
    conn.close()
    try:

        conn = sqlite3.connect(ATTENDANCE_DATABASE_PATH)
        cursor = conn.cursor()
        # JSON dosyasından verileri okuyun
        with open('new_students_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Verileri tabloya ekleyin
        for student in data["students"]:
            name = student.get("name", "")
            last_name = student.get("last_name", "")
            student_number = student.get("student_number", "")
            card_id = student.get("card_id", "")
            lessons = json.dumps([
                "BILP-113", "BILP-107.1", "BILP-107.2", "BILP-109", "BILP-114.1", "BILP-114.2", "BILP-105", "BILP-201",
                "BILP-217", "BILP-213", "BILP-215", "BILP-207", "BILP-216", "BILP-213", "BILP-226", "BILP-209",
                "BILP-116", "BILP-221", "BILP-108", "BILP-106", "BILP-219", "BILP-110"
            ])

            cursor.execute(
                "INSERT OR IGNORE INTO students (name, last_name, student_number, card_id, lessons) VALUES (?, ?, ?, ?, ?)",
                (name, last_name, student_number, card_id, lessons))


        cursor.execute('''
            INSERT OR IGNORE INTO instructors (name, last_name, card_id, schedule)
            VALUES (?, ?, ?, ?)
            ''', ("Samet", "ATABAŞ", "d56ef659",
                  json.dumps({
                      "0": {
                          "BILP-113": [[8, 0], [10, 0]],
                          "BILP-114.1": [[10, 0], [12, 0]],
                          "BILP-114.2": [[15, 0], [17, 0]]
                      },
                      "1": {},
                      "2": {
                          "BILP-107.1": [[8, 0], [10, 0]],
                          "BILP-107.2": [[10, 0], [12, 0]]
                      },
                      "3": {
                          "HİT-105": [[9, 0], [16, 0]]
                      },
                      "4": {},
                      "5": {},
                      "6": {}
                  })
                  )
                       )

        cursor.executemany('''
            INSERT OR IGNORE INTO lessons (name, code, class_hours)
            VALUES (?, ?, ?)
            ''', [
            ('Bilgisayar Donanımı', 'BILP-113', 4),
            ('Grafik ve Animasyon', 'BILP-107', 4),
            ('Sunucu İşletim Sistemi', 'BILP-114', 2)
        ])
        conn.commit()
        conn.close()
        print("Tablolara örnek ilk veriler eklendi")
    except sqlite3.Error as e:
        print(e)


def set_secret_key():
    # .env dosyasını oku ve mevcut değerleri al
    existing_env_values = {}
    with open('.env', 'r') as env_file:
        for line in env_file:
            line = line.strip()
            if line:
                key, value = line.split('=', 1)
                existing_env_values[key] = value

    # Güçlü bir secret_key oluştur
    secret_key = secrets.token_urlsafe(32)

    # .env dosyasına yeni secret_key değerini ekle
    existing_env_values['SECRET_KEY'] = secret_key

    # .env dosyasını güncelle
    with open('.env', 'w') as env_file:
        for key, value in existing_env_values.items():
            env_file.write(f"{key}={value}\n")

    # Environment değişkenine de secret_key'i ekleyelim
    os.environ['SECRET_KEY'] = secret_key

    print("Secret key .env dosyasına eklenmiştir.")


def main():
    set_secret_key()
    create_tables()
    insert_initial_data()
