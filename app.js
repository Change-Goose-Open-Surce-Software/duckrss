// DuckRSS - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Passwort-Felder dynamisch hinzufügen
    const addPasswordBtn = document.getElementById('add-password');
    if (addPasswordBtn) {
        addPasswordBtn.addEventListener('click', function() {
            const container = document.getElementById('password-container');
            const count = container.children.length + 1;
            
            if (count <= 10) {
                const div = document.createElement('div');
                div.className = 'password-field';
                div.innerHTML = `
                    <label>Passwort ${count}:</label>
                    <input type="password" name="password_${count}" placeholder="Passwort ${count}">
                `;
                container.appendChild(div);
            }
        });
    }
    
    // Formular-Validierung
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = '#ff0000';
                } else {
                    field.style.borderColor = '#00ff00';
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Bitte alle erforderlichen Felder ausfüllen!');
            }
        });
    });
    
    // Feed URL kopieren
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            navigator.clipboard.writeText(url).then(() => {
                const originalText = this.textContent;
                this.textContent = '✓ Kopiert!';
                setTimeout(() => {
                    this.textContent = originalText;
                }, 2000);
            });
        });
    });
    
    // Confirm Delete
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Wirklich löschen?')) {
                e.preventDefault();
            }
        });
    });
    
    // Terminal Effekt für Logging
    const terminal = document.getElementById('terminal');
    if (terminal) {
        setInterval(() => {
            const timestamp = new Date().toISOString();
            const messages = [
                'Feeds aktualisieren...',
                'Eingang verarbeiten...',
                'RSS generieren...',
                'Bereit.'
            ];
            const msg = messages[Math.floor(Math.random() * messages.length)];
            
            const line = document.createElement('div');
            line.textContent = `[${timestamp}] ${msg}`;
            terminal.appendChild(line);
            
            // Nur letzte 10 Zeilen behalten
            while (terminal.children.length > 10) {
                terminal.removeChild(terminal.firstChild);
            }
        }, 3000);
    }
});

// Funktion zum Teilen eines Items
function shareItem(itemId) {
    const outputId = document.getElementById(`share-output-${itemId}`).value;
    if (outputId) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/feeds/${itemId}/share`;
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'output_id';
        input.value = outputId;
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    }
}

// ASCII Animation
function animateASCII(element) {
    const frames = [
        '( o.o)',
        '( O.O)',
        '( -.- )',
        '( o.o)'
    ];
    let currentFrame = 0;
    
    setInterval(() => {
        if (element) {
            element.textContent = frames[currentFrame];
            currentFrame = (currentFrame + 1) % frames.length;
        }
    }, 500);
}

// Bei Seitenlade ASCII-Ente animieren
const duck = document.getElementById('ascii-duck');
if (duck) {
    animateASCII(duck);
}
