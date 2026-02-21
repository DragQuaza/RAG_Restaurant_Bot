import sqlite3
import json
from datetime import datetime

DB_FILE = "restaurant.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create Bookings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone_number TEXT,
            number_of_guests INTEGER,
            date TEXT,
            time TEXT,
            special_requests TEXT,
            status TEXT DEFAULT 'Confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Conversation Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_booking(customer_name, phone_number, number_of_guests, date, time, special_requests=""):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bookings (customer_name, phone_number, number_of_guests, date, time, special_requests)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (customer_name, phone_number, number_of_guests, date, time, special_requests))
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return booking_id

def get_booking(booking_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE booking_id = ?', (booking_id,))
    booking = cursor.fetchone()
    conn.close()
    return booking

def cancel_booking(booking_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE booking_id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def modify_booking(booking_id, **kwargs):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.append(booking_id)
    query = f"UPDATE bookings SET {set_clause} WHERE booking_id = ?"
    cursor.execute(query, tuple(values))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def log_message(session_id, role, content):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversation_history (session_id, role, content)
        VALUES (?, ?, ?)
    ''', (session_id, role, content))
    conn.commit()
    conn.close()
    
def get_conversation_history(session_id, limit=10):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content FROM conversation_history 
        WHERE session_id = ? 
        ORDER BY created_at ASC LIMIT ?
    ''', (session_id, limit))
    history = cursor.fetchall()
    conn.close()
    return history
