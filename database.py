#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuckRSS - Datenbank Verwaltung
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = 'data/duckrss.db'

def get_db():
    """Datenbankverbindung herstellen"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Datenbank initialisieren"""
    os.makedirs('data', exist_ok=True)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Benutzer Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Passwörter Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Passkeys Tabelle (WebAuthn)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passkeys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            credential_id TEXT UNIQUE NOT NULL,
            public_key TEXT NOT NULL,
            sign_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Sicherheitsanforderungen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_requirements (
            user_id INTEGER PRIMARY KEY,
            required_passwords INTEGER DEFAULT 1,
            required_passkeys INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Eingänge (externe RSS Feeds)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            feed_url TEXT NOT NULL,
            last_fetch TIMESTAMP,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Ausgänge (eigene RSS Feeds)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            description TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Verknüpfung Eingänge -> Ausgänge
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS input_output_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_id INTEGER NOT NULL,
            output_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(input_id, output_id),
            FOREIGN KEY (input_id) REFERENCES inputs(id) ON DELETE CASCADE,
            FOREIGN KEY (output_id) REFERENCES outputs(id) ON DELETE CASCADE
        )
    ''')
    
    # Feed Items (gecachte Artikel)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feed_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_id INTEGER,
            user_id INTEGER,
            guid TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            link TEXT,
            description TEXT,
            content TEXT,
            author TEXT,
            published TIMESTAMP,
            is_custom INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (input_id) REFERENCES inputs(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Feed Items -> Ausgänge Zuordnung
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_output_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            output_id INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(item_id, output_id),
            FOREIGN KEY (item_id) REFERENCES feed_items(id) ON DELETE CASCADE,
            FOREIGN KEY (output_id) REFERENCES outputs(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✓ Datenbank initialisiert:", DB_PATH)

if __name__ == '__main__':
    init_db()
