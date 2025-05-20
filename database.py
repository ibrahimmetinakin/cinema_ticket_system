import sqlite3
from sqlite3 import Error
import hashlib
import re
import logging
from datetime import datetime, timedelta


# 🔧 Logging Ayarları
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 📂 Veritabanı Ayarı
DB_NAME = "cinema_system.db"
RESERVATION_TIMEOUT_MINUTES = 15  # Rezervasyon Süresi

def create_connection():
    try:
        return sqlite3.connect(DB_NAME)
    except Error as e:
        logging.error(f"Veritabanı bağlantı hatası: {e}")
    return None

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            film_name TEXT NOT NULL,
            theater_name TEXT NOT NULL,
            seat_number TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS films (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image_file TEXT NOT NULL,
            trailer_path TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            film_name TEXT NOT NULL,
            theater_name TEXT NOT NULL,
            seat_number TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            reserved_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    conn.close()

def add_trailer_column_if_missing():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(films);")
    columns = [col[1] for col in cursor.fetchall()]
    if "trailer_path" not in columns:
        cursor.execute("ALTER TABLE films ADD COLUMN trailer_path TEXT;")
        conn.commit()
    conn.close()

create_tables()
add_trailer_column_if_missing()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def create_user(username, password, email):
    if not is_valid_email(email):
        logging.warning("Geçersiz e-posta adresi!")
        return False

    conn = create_connection()
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?);",
                       (username, hashed_password, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?;", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_user_info(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
    user_info = cursor.fetchone()
    conn.close()
    return user_info

def update_user_password(username, old_password, new_password):
    if not check_user(username, old_password):
        return False
    conn = create_connection()
    cursor = conn.cursor()
    hashed_new = hash_password(new_password)
    cursor.execute("UPDATE users SET password = ? WHERE username = ?;", (hashed_new, username))
    conn.commit()
    conn.close()
    return True


def add_film(name, image_file, trailer_path=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO films (name, image_file, trailer_path) VALUES (?, ?, ?);",
                   (name, image_file, trailer_path))
    conn.commit()
    conn.close()

def get_all_films():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, image_file, trailer_path FROM films;")
    films = cursor.fetchall()
    conn.close()
    return films

def save_ticket(username, film_name, theater_name, seat_number, date, time):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?;", (username,))
    user = cursor.fetchone()
    if user is None:
        conn.close()
        return False

    user_id = user[0]

    cursor.execute("""
        SELECT * FROM tickets WHERE film_name = ? AND theater_name = ? 
        AND seat_number = ? AND date = ? AND time = ?;
    """, (film_name, theater_name, seat_number, date, time))

    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute("""
        INSERT INTO tickets (user_id, film_name, theater_name, seat_number, date, time)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (user_id, film_name, theater_name, seat_number, date, time))

    cursor.execute("""
        DELETE FROM reservations WHERE seat_number = ? AND film_name = ? AND theater_name = ? 
        AND date = ? AND time = ?;
    """, (seat_number, film_name, theater_name, date, time))

    conn.commit()
    conn.close()
    return True

def get_user_tickets(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?;", (username,))
    user = cursor.fetchone()
    if user is None:
        conn.close()
        return []

    user_id = user[0]
    cursor.execute("""
        SELECT film_name, theater_name, seat_number, date, time 
        FROM tickets WHERE user_id = ?;
    """, (user_id,))
    tickets = cursor.fetchall()
    conn.close()
    return tickets

def get_reserved_seats(film_name, theater_name, date, time):
    cleanup_expired_reservations()
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT seat_number FROM tickets 
        WHERE film_name = ? AND theater_name = ? AND date = ? AND time = ?;
    """, (film_name, theater_name, date, time))
    sold = {row[0] for row in cursor.fetchall()}

    cursor.execute("""
        SELECT seat_number FROM reservations 
        WHERE film_name = ? AND theater_name = ? AND date = ? AND time = ?;
    """, (film_name, theater_name, date, time))
    reserved = {row[0] for row in cursor.fetchall()}

    conn.close()
    return sold, reserved

def cancel_reservation(username, film_name, theater_name, seat_number, date, time):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?;", (username,))
    user = cursor.fetchone()
    if user is None:
        conn.close()
        return False

    user_id = user[0]

    cursor.execute("""
        DELETE FROM reservations 
        WHERE user_id = ? AND film_name = ? AND theater_name = ? 
        AND seat_number = ? AND date = ? AND time = ?;
    """, (user_id, film_name, theater_name, seat_number, date, time))

    conn.commit()
    conn.close()
    return True

def cancel_ticket(username, film_name, theater_name, seat_number, date, time):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM tickets 
        WHERE film_name = ? AND theater_name = ? AND seat_number = ? 
        AND date = ? AND time = ?;
    """, (film_name, theater_name, seat_number, date, time))
    conn.commit()
    conn.close()

def reserve_seat(username, film_name, theater_name, seat_number, date, time):
    cleanup_expired_reservations()
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?;", (username,))
    user = cursor.fetchone()
    if user is None:
        conn.close()
        return False

    user_id = user[0]

    cursor.execute("""
        SELECT * FROM tickets WHERE film_name = ? AND theater_name = ? 
        AND seat_number = ? AND date = ? AND time = ?;
    """, (film_name, theater_name, seat_number, date, time))
    if cursor.fetchone():
        conn.close()
        return False

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT OR REPLACE INTO reservations (user_id, film_name, theater_name, seat_number, date, time, reserved_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (user_id, film_name, theater_name, seat_number, date, time, now))

    conn.commit()
    conn.close()
    return True

def cleanup_expired_reservations():
    conn = create_connection()
    cursor = conn.cursor()
    expiration_time = (datetime.now() - timedelta(minutes=RESERVATION_TIMEOUT_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("DELETE FROM reservations WHERE reserved_at < ?;", (expiration_time,))
    conn.commit()
    conn.close()

def preload_films():
    create_tables()
    add_trailer_column_if_missing()

sample_films = [
    ("Örümcek-Adam 2", "1-Örümcek-Adam 2.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\1-Orumcek-Adam 2 Spider-Man 2 - 2004 - Sinemalar com.mp4"),
    ("Son Durak Kan Bağı", "2-Son Durak Kan Bağı.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\2-Son Durak Kan Bagı.mp4"),
    ("Haydi Tut Elimi", "3-Haydi Tut Elimi.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\3-Haydi Tut Elimi Filmi Bilet Al Paribu Cineverse.mp4"),
    ("Dehşet Ekranı Habis Ruh", "4-Dehşet Ekranı Habis Ruh.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\4-Dehşet Ekranı Habis Ruh.mp4"),
    ("Parmak Çocuk Emma", "5-Parmak Çocuk Emma.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\5-parmak çocuk emma.mp4"),
    ("Orman Çocukları", "6-Orman Çocukları.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\6-orman çocukları.mp4"),
    ("Sıcak Büfe", "7-Sıcak Büfe.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\7-sıcak büfe.mp4"),
    ("Gülizar", "8-Gülizar.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\8-gülizar.mp4"),
    ("Ayak Takımı", "9-Ayak Takımı.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\9-ayak takımı.mp4"),
    ("Hurry Up Tomorrow", "10-Hurry Up Tomorrow.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\10-hurry up tomorrow.mp4"),
    ("Baba", "11-Baba.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\11-baba.mp4"),
    ("Örümcek-Adam", "12-Örümcek-Adam.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\12-örümcek adam.mp4"),
    ("Evli Mutlu Çocuklu", "13-Evli Mutlu Çocuklu.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\13-evli mutlu çocuklu.mp4"),
    ("Popeye the Slayer Man", "14-Popeye the Slayer Man.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\14-popeye the slayer man.mp4"),
    ("Efendiler", "15-Efendiler.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\15-efendiler.mp4"),
    ("Diş Perisi Masalı", "16-Diş Perisi Masalı.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\16-Diş Perisi Masalı.mp4"),
    ("Sonradan Gurme", "17-Sonradan Gurme.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\17-Sonradan Gurme.mp4"),
    ("Saint-Ex", "18-Saint-Ex.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\18-Saint-Ex.mp4"),
    ("Kaçak Fil", "19-Kaçak Fil.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\19-Kaçak Fil.mp4"),
    ("Thunderbolts", "20-Thunderbolts.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\20-Thunderbolts.mp4"),
    ("Köstebekgiller Ata Tohumu Muhafızları", "21-Köstebekgiller Ata Tohumu Muhafızları.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\21-Köstebekgiller Ata Tohumu Muhafızları.mp4"),
    ("Aznavour", "22-Aznavour.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\22-Aznavour.mp4"),
    ("Ölü Mevsim", "23-Ölü Mevsim.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\23-Ölü Mevsim.mp4"),
    ("Kafka Hayatımın Aşkı", "24-Kafka Hayatımın Aşkı.jpg", r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\movie trailers\24-Kafka hayatımın aşkı.mp4")
]

conn = create_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM films;")
if cursor.fetchone()[0] == 0:
    cursor.executemany("INSERT INTO films (name, image_file, trailer_path) VALUES (?, ?, ?);", sample_films)
    conn.commit()
conn.close()


def get_user_reservations(username):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?;", (username,))
    user = cursor.fetchone()
    if user is None:
        conn.close()
        return []

    user_id = user[0]
    cursor.execute("""
        SELECT film_name, theater_name, seat_number, date, time 
        FROM reservations WHERE user_id = ?;
    """, (user_id,))
    reservations = cursor.fetchall()
    conn.close()
    return reservations




