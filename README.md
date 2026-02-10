# 🦆 DuckRSS - Retro RSS Feed Manager

Ein selbst-gehosteter RSS Feed Manager im Retro-Terminal-Style für Debian-Server.

## Features

### 🔐 Sicherheit
- Multi-Faktor-Authentifizierung mit Passwörtern und Passkeys
- Konfigurierbare Sicherheitsanforderungen (z.B. 0 PW + 2 PK oder 5 PW + 1 PK)
- Sichere Passwort-Verschlüsselung mit bcrypt
- Sicherheit nur für Admin-Funktionen, öffentliche Feeds bleiben offen

### 📥 Eingänge (Externe RSS Feeds)
- Externe RSS Feeds hinzufügen und verwalten
- Feeds automatisch abrufen und cachen
- Mehrere Eingänge in einen Ausgang kombinieren

### 📤 Ausgänge (Eigene RSS Feeds)
- Eigene RSS Feeds erstellen und hosten
- Öffentliche URLs für jeden Feed
- Kombiniert Inhalte aus mehreren Quellen

### ✏️ RSS Editor
- Eigene Feed-Artikel erstellen
- In mehreren Ausgängen veröffentlichen
- Perfekt für lokale Redakteure, Blogger, Projekt-Updates

### 🔄 Feed-Verwaltung
- Alle Feed-Items in einer Übersicht
- Items zwischen Ausgängen teilen
- Anzeige der Herkunft (Eingang) und Ziele (Ausgänge)

### 🎨 Retro-Design
- Terminal-inspiriertes Design
- Grün-auf-Schwarz Farbschema
- Responsive für Desktop und Mobile

## Installation

### Voraussetzungen
- Debian/Ubuntu Server
- Root-Zugriff (sudo)

### Automatische Installation

```bash
# Repository klonen oder Dateien herunterladen
cd duckrss

# Installationsskript ausführen
chmod +x install.sh
sudo ./install.sh
```

Das Script installiert alle benötigten Pakete via APT (kein pip!):
- python3
- python3-flask
- python3-feedparser
- python3-bcrypt
- python3-requests
- python3-lxml
- sqlite3

### Server starten

#### Als Systemd Service (empfohlen)
```bash
sudo systemctl start duckrss
sudo systemctl status duckrss
```

#### Manuell
```bash
python3 app.py
```

Der Server läuft dann auf: http://localhost:5000

### Externe Erreichbarkeit

Für Zugriff von außen (z.B. mit DuckDNS):

1. Port 5000 in der Firewall öffnen:
```bash
sudo ufw allow 5000
```

2. DuckDNS oder andere Dynamic DNS einrichten

3. Optional: Nginx Reverse Proxy für Port 80/443

## Verwendung

### 1. Konto erstellen
- Navigiere zu http://your-server:5000
- Klicke auf "Registrieren"
- Wähle Benutzername
- Konfiguriere Sicherheit (z.B. 2 Passwörter + 0 Passkeys)
- Gebe die erforderlichen Passwörter ein

### 2. Eingänge hinzufügen
- Gehe zu "Eingänge"
- Klicke "Neuen Eingang erstellen"
- Name: z.B. "Internationale Nachrichten"
- Feed URL: z.B. http://seite.web/news/feed
- Optional: Direkt zu Ausgängen hinzufügen
- Klicke "Feed abrufen" um Artikel zu laden

### 3. Ausgänge erstellen
- Gehe zu "Ausgänge"
- Klicke "Neuen Ausgang erstellen"
- Name: z.B. "Nachrichten"
- Beschreibung: Optional
- Erhalte öffentliche URL: http://your-server:5000/exit/nachrichten.xml

### 4. Eigene Artikel schreiben
- Gehe zu "Editor"
- Schreibe Titel und Inhalt
- Wähle Ausgänge für Veröffentlichung
- Klicke "Artikel veröffentlichen"

### 5. Feed abonnieren
- Kopiere die Feed URL aus "Ausgänge"
- Füge sie in deinen RSS Reader ein (z.B. Gnome Feeds, Feedly)
- Oder teile die URL mit anderen

## Dateistruktur

```
duckrss/
├── install.sh              # Installations-Script
├── app.py                  # Haupt-Flask-Anwendung
├── database.py             # Datenbank-Verwaltung
├── auth.py                 # Authentifizierung
├── rss_manager.py          # RSS Feed-Logik
├── static/
│   ├── css/
│   │   └── retro.css      # Retro-Styling
│   └── js/
│       └── app.js         # Client-JavaScript
├── templates/
│   ├── base.html          # Basis-Template
│   ├── login.html         # Login
│   ├── register.html      # Registrierung
│   ├── dashboard.html     # Dashboard
│   ├── inputs.html        # Eingänge
│   ├── outputs.html       # Ausgänge
│   ├── feeds.html         # Alle Feeds
│   └── editor.html        # RSS Editor
└── data/
    └── duckrss.db         # SQLite Datenbank

```

## Beispiel-Workflow: Lokaler Redakteur

1. Füge regionale News-Feeds als Eingänge hinzu
2. Erstelle Ausgang "Lokale + Regionale Nachrichten"
3. Verknüpfe die regionalen Eingänge mit dem Ausgang
4. Schreibe eigene lokale Berichte im Editor
5. Veröffentliche sie im selben Ausgang
6. Teile die Feed-URL in der Nachbarschaft
7. Bewohner haben lokale + regionale Nachrichten in einem Feed

## Verwendete Technologien

- **Backend**: Python 3 mit Flask
- **Datenbank**: SQLite
- **RSS Parsing**: python3-feedparser
- **Sicherheit**: bcrypt für Passwort-Hashing
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Terminal/Retro-Ästhetik

## Systemd Service

Der Installer erstellt automatisch einen systemd Service:

```bash
# Starten
sudo systemctl start duckrss

# Stoppen
sudo systemctl stop duckrss

# Status prüfen
sudo systemctl status duckrss

# Logs ansehen
sudo journalctl -u duckrss -f

# Autostart aktivieren
sudo systemctl enable duckrss

# Autostart deaktivieren
sudo systemctl disable duckrss
```

## Sicherheitshinweise

- Ändere den Flask `secret_key` in `app.py` für Produktivumgebung
- Verwende HTTPS in Produktion (z.B. mit Nginx + Let's Encrypt)
- Öffentliche Feeds (URLs unter /exit/) haben keine Authentifizierung
- Admin-Funktionen (Erstellen, Bearbeiten, Löschen) sind geschützt

## Fehlerbehebung

### Server startet nicht
```bash
# Prüfe Logs
sudo journalctl -u duckrss -n 50

# Prüfe ob Port 5000 frei ist
sudo netstat -tulpn | grep 5000

# Manuell starten für Debug
python3 app.py
```

### Datenbank-Fehler
```bash
# Datenbank neu initialisieren
cd duckrss
python3 database.py
```

### Feed kann nicht abgerufen werden
- Prüfe Internet-Verbindung
- Prüfe ob Feed-URL korrekt ist
- Prüfe Firewall-Einstellungen

## Lizenz

Open Source - Frei verwendbar und anpassbar

## Support

Bei Problemen oder Fragen:
1. Prüfe die Logs: `sudo journalctl -u duckrss -f`
2. Prüfe die README
3. Erstelle ein Issue im Repository

---

**Made with 🦆 and ❤️ for the Retro Computing Community**
