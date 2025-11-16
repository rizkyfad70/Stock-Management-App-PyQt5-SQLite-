import sqlite3
import hashlib

DB_PATH = 'db/stok.db'  # Lokasi file database

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def check_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    hashed = hash_password(password)
    cursor.execute("SELECT * FROM user_data WHERE nama=? AND pass=?", (username, hashed))
    result = cursor.fetchone()
    conn.close()
    return result

def user_exists(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_data WHERE nama=?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    hashed = hash_password(password)
    cursor.execute("INSERT INTO user_data (nama, pass) VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()
