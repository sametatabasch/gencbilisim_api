from dotenv import load_dotenv
import sqlite3
import os
from werkzeug.security import generate_password_hash

load_dotenv()

DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'mydatabase.db'


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


def main():
    create_tables()
    insert_initial_data()
