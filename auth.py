#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuckRSS - Authentifizierung
"""

import bcrypt
import secrets
from database import get_db

class Auth:
    @staticmethod
    def hash_password(password):
        """Passwort hashen"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """Passwort verifizieren"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def create_user(username, passwords=None, required_passwords=1, required_passkeys=0):
        """Neuen Benutzer erstellen"""
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # Benutzer anlegen
            cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
            user_id = cursor.lastrowid
            
            # Sicherheitsanforderungen setzen
            cursor.execute('''
                INSERT INTO security_requirements (user_id, required_passwords, required_passkeys)
                VALUES (?, ?, ?)
            ''', (user_id, required_passwords, required_passkeys))
            
            # Passwörter hinzufügen
            if passwords:
                for password in passwords:
                    password_hash = Auth.hash_password(password)
                    cursor.execute('''
                        INSERT INTO passwords (user_id, password_hash)
                        VALUES (?, ?)
                    ''', (user_id, password_hash))
            
            conn.commit()
            return user_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def verify_user(username, passwords=None):
        """Benutzer verifizieren"""
        conn = get_db()
        cursor = conn.cursor()
        
        # Benutzer laden
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return None
        
        user_id = user['id']
        
        # Sicherheitsanforderungen laden
        cursor.execute('SELECT * FROM security_requirements WHERE user_id = ?', (user_id,))
        requirements = cursor.fetchone()
        
        required_passwords = requirements['required_passwords'] if requirements else 1
        required_passkeys = requirements['required_passkeys'] if requirements else 0
        
        # Passwörter prüfen
        if required_passwords > 0 and passwords:
            cursor.execute('SELECT password_hash FROM passwords WHERE user_id = ?', (user_id,))
            stored_hashes = [row['password_hash'] for row in cursor.fetchall()]
            
            if len(passwords) < required_passwords:
                conn.close()
                return None
            
            verified_count = 0
            for password in passwords:
                for stored_hash in stored_hashes:
                    if Auth.verify_password(password, stored_hash):
                        verified_count += 1
                        break
            
            if verified_count < required_passwords:
                conn.close()
                return None
        
        # TODO: Passkeys prüfen (WebAuthn implementierung)
        # Für jetzt: wenn keine Passkeys erforderlich oder nur Passwörter
        
        conn.close()
        return dict(user)
    
    @staticmethod
    def get_user_by_id(user_id):
        """Benutzer anhand ID laden"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def get_security_requirements(user_id):
        """Sicherheitsanforderungen laden"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM security_requirements WHERE user_id = ?', (user_id,))
        reqs = cursor.fetchone()
        conn.close()
        return dict(reqs) if reqs else {'required_passwords': 1, 'required_passkeys': 0}
