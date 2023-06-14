from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()

DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'mydatabase.db'


def create_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
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
        INSERT OR IGNORE INTO users (name, email, password, active)
        VALUES (?, ?, ?, ?)
    ''', ('Samet ATABAŞ', 'sametatabasch@gmail.com', '123456', 1))

    # Add Relays
    relays = [
        (0, 'relay1'),
        (0, 'relay2')
    ]
    cursor.execute('''INSERT OR IGNORE INTO relays(status,name) VALUES(?,?);
    ''', relays)

    conn.commit()
    conn.close()


create_tables()
insert_initial_data()
