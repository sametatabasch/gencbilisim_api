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
            student_id TEXT,
            card_id TEXT,
            UNIQUE(student_id),
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
                attendance TEXT,
                UNIQUE(code)
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
        cursor.executemany('''
                INSERT OR IGNORE INTO students (name, last_name, student_id, card_id)
                VALUES (?, ?, ?, ?)
            ''', [
            ('Samet', 'ATABAŞ', '090606043', '93bdd50b'),
            ('Kart', ' Bir', '090606044', '3413fc51'),
            ('Kart', ' İki', '090606045', '2aca190b'),
            ('Diş', ' KTÜ', '090606046', 'd226d935'),
        ])

        cursor.execute('''
            INSERT OR IGNORE INTO instructors (name, last_name, card_id, schedule)
            VALUES (?, ?, ?, ?)
            ''', ("Samet", "ATABAŞ", "d56ef659",
                  json.dumps({
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

                      }})
                  )
                       )

        cursor.executemany('''
            INSERT OR IGNORE INTO lessons (name, code, attendance)
            VALUES (?, ?, ?)
            ''', [
            ('Mathematics', 'MATH101', json.dumps(
                {
                    1: [
                        {"card_id": "93bdd50b", "student_id": "090606043"},
                        {"card_id": "3413fc51", "student_id": "090606044"}
                    ],
                    2: [
                        {"card_id": "93bdd50b", "student_id": "090606043"}
                    ]
                }
            )),
            ('Physics', 'PHYS201', json.dumps(
                {
                    1: [
                        {"card_id": "93bdd50b", "student_id": "090606043"},
                        {"card_id": "3413fc51", "student_id": "090606044"}
                    ],
                    2: [
                        {"card_id": "93bdd50b", "student_id": "090606043"}
                    ]
                }
            )),
            ('Chemistry', 'CHEM301', json.dumps(
                {
                    1: [
                        {"card_id": "93bdd50b", "student_id": "090606043"},
                        {"card_id": "3413fc51", "student_id": "090606044"}
                    ],
                    2: [
                        {"card_id": "93bdd50b", "student_id": "090606043"}
                    ]
                }
            ))
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
