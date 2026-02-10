#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuckRSS - Haupt-Anwendung
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import secrets
from auth import Auth
from rss_manager import RSSManager
from database import get_db

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ============== Hilfsfunktionen ==============

def login_required(f):
    """Decorator für geschützte Routen"""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# ============== Authentifizierung ==============

@app.route('/')
def index():
    """Startseite"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registrierung"""
    if request.method == 'POST':
        username = request.form.get('username')
        required_passwords = int(request.form.get('required_passwords', 1))
        required_passkeys = int(request.form.get('required_passkeys', 0))
        
        # Passwörter sammeln
        passwords = []
        for i in range(1, 11):  # Max 10 Passwörter
            pw = request.form.get(f'password_{i}')
            if pw:
                passwords.append(pw)
        
        if len(passwords) < required_passwords:
            return render_template('register.html', 
                error=f'Bitte mindestens {required_passwords} Passwörter angeben')
        
        try:
            user_id = Auth.create_user(username, passwords, required_passwords, required_passkeys)
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('register.html', error='Benutzername bereits vergeben')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Anmeldung"""
    if request.method == 'POST':
        username = request.form.get('username')
        
        # Passwörter sammeln
        passwords = []
        for i in range(1, 11):
            pw = request.form.get(f'password_{i}')
            if pw:
                passwords.append(pw)
        
        user = Auth.verify_user(username, passwords)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', 
                error='Anmeldung fehlgeschlagen. Prüfen Sie Benutzername und Passwörter.')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Abmelden"""
    session.clear()
    return redirect(url_for('login'))

# ============== Dashboard ==============

@app.route('/dashboard')
@login_required
def dashboard():
    """Hauptdashboard"""
    user_id = session['user_id']
    inputs = RSSManager.get_inputs(user_id)
    outputs = RSSManager.get_outputs(user_id)
    
    return render_template('dashboard.html', 
        username=session['username'],
        inputs=inputs,
        outputs=outputs)

# ============== Eingänge ==============

@app.route('/inputs')
@login_required
def inputs():
    """Eingänge verwalten"""
    user_id = session['user_id']
    inputs = RSSManager.get_inputs(user_id)
    outputs = RSSManager.get_outputs(user_id)
    
    return render_template('inputs.html', 
        inputs=inputs,
        outputs=outputs)

@app.route('/inputs/create', methods=['POST'])
@login_required
def create_input():
    """Neuen Eingang erstellen"""
    user_id = session['user_id']
    name = request.form.get('name')
    feed_url = request.form.get('feed_url')
    
    input_id = RSSManager.create_input(user_id, name, feed_url)
    
    # Optional: zu Ausgängen hinzufügen
    output_ids = request.form.getlist('output_ids')
    for output_id in output_ids:
        RSSManager.link_input_to_output(input_id, int(output_id))
    
    return redirect(url_for('inputs'))

@app.route('/inputs/<int:input_id>/fetch', methods=['POST'])
@login_required
def fetch_input(input_id):
    """Feed aktualisieren"""
    RSSManager.fetch_feed(input_id)
    return redirect(url_for('inputs'))

@app.route('/inputs/<int:input_id>/link', methods=['POST'])
@login_required
def link_input(input_id):
    """Eingang zu Ausgang verknüpfen"""
    output_ids = request.form.getlist('output_ids')
    for output_id in output_ids:
        RSSManager.link_input_to_output(input_id, int(output_id))
    return redirect(url_for('inputs'))

# ============== Ausgänge ==============

@app.route('/outputs')
@login_required
def outputs():
    """Ausgänge verwalten"""
    user_id = session['user_id']
    outputs = RSSManager.get_outputs(user_id)
    
    # Base URL aus Request
    base_url = request.host_url.rstrip('/')
    
    return render_template('outputs.html', 
        outputs=outputs,
        base_url=base_url)

@app.route('/outputs/create', methods=['POST'])
@login_required
def create_output():
    """Neuen Ausgang erstellen"""
    user_id = session['user_id']
    name = request.form.get('name')
    description = request.form.get('description', '')
    
    RSSManager.create_output(user_id, name, description)
    return redirect(url_for('outputs'))

# ============== Feed Items ==============

@app.route('/feeds')
@login_required
def feeds():
    """Alle Feed-Items anzeigen"""
    user_id = session['user_id']
    items = RSSManager.get_all_items(user_id)
    outputs = RSSManager.get_outputs(user_id)
    
    return render_template('feeds.html', 
        items=items,
        outputs=outputs)

@app.route('/feeds/<int:item_id>/share', methods=['POST'])
@login_required
def share_item(item_id):
    """Item zu Ausgang teilen"""
    output_id = request.form.get('output_id')
    RSSManager.share_item_to_output(item_id, int(output_id))
    return redirect(url_for('feeds'))

# ============== Editor ==============

@app.route('/editor')
@login_required
def editor():
    """Feed-Editor"""
    user_id = session['user_id']
    outputs = RSSManager.get_outputs(user_id)
    
    return render_template('editor.html', outputs=outputs)

@app.route('/editor/create', methods=['POST'])
@login_required
def create_custom_feed():
    """Eigenen Feed-Artikel erstellen"""
    user_id = session['user_id']
    title = request.form.get('title')
    content = request.form.get('content')
    output_ids = [int(x) for x in request.form.getlist('output_ids')]
    
    RSSManager.create_custom_item(user_id, title, content, output_ids)
    return redirect(url_for('editor'))

# ============== Öffentliche RSS Feeds ==============

@app.route('/exit/<slug>.xml')
def rss_feed(slug):
    """Öffentlicher RSS Feed (keine Authentifizierung!)"""
    xml = RSSManager.get_output_feed(slug)
    
    if xml:
        return Response(xml, mimetype='application/rss+xml')
    else:
        return 'Feed nicht gefunden', 404

# ============== Server starten ==============

if __name__ == '__main__':
    from database import init_db
    init_db()
    
    print("")
    print("=" * 50)
    print("   🦆 DuckRSS Server gestartet")
    print("=" * 50)
    print("")
    print("   URL: http://localhost:5000")
    print("")
    print("   Strg+C zum Beenden")
    print("")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
