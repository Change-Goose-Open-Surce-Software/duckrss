#!/bin/bash
# DuckRSS Installationsscript für Debian
# Nur mit APT-Paketen

echo "================================"
echo "   DuckRSS Installation         "
echo "================================"
echo ""

# Root-Rechte prüfen
if [ "$EUID" -ne 0 ]; then 
    echo "Bitte als root ausführen (sudo ./install.sh)"
    exit 1
fi

echo "[1/5] System aktualisieren..."
apt update

echo ""
echo "[2/5] Benötigte Pakete installieren..."
apt install -y \
    python3 \
    python3-flask \
    python3-feedparser \
    python3-bcrypt \
    python3-requests \
    python3-lxml \
    sqlite3

echo ""
echo "[3/5] Datenbank initialisieren..."
sudo -u $SUDO_USER python3 database.py

echo ""
echo "[4/5] Berechtigungen setzen..."
chown -R $SUDO_USER:$SUDO_USER .
chmod +x app.py
chmod 755 data
chmod 644 data/duckrss.db 2>/dev/null || true

echo ""
echo "[5/5] Systemd Service erstellen..."
cat > /etc/systemd/system/duckrss.service << EOF
[Unit]
Description=DuckRSS Feed Manager
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable duckrss.service

echo ""
echo "================================"
echo "✓ Installation abgeschlossen!"
echo "================================"
echo ""
echo "Starten: sudo systemctl start duckrss"
echo "Status:  sudo systemctl status duckrss"
echo "Stoppen: sudo systemctl stop duckrss"
echo ""
echo "Oder manuell: python3 app.py"
echo ""
echo "Weboberfläche: http://localhost:5000"
echo ""
