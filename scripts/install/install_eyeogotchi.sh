#!/usr/bin/env bash
#
# Eyeogotchi Installer
# Sets up aliases, directories, Python environment, systemd service, and log paths.
#

set -e

EYE_DIR="$HOME/.vscode-projects/Eyeogotchi"
VENV_DIR="$EYE_DIR/.venv"
BASE_DIR="os.path.expanduser("~/.eyeogotchi/logs")"
LOGFILE="os.path.join($BASE_DIR, "eyeogotchi.log")"
SERVICE_FILE="/etc/systemd/system/eyeogotchi.service"
BASHRC="$HOME/.bashrc"

echo "=== Eyeogotchi Installer ==="
echo "Installing from: $EYE_DIR"
echo ""

# ------------------------------------------------------------
# PYTHON ENVIRONMENT
# ------------------------------------------------------------
echo "[1/6] Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r "$EYE_DIR/requirements.txt" || true

# ------------------------------------------------------------
# LOG DIRECTORY
# ------------------------------------------------------------
echo "[2/6] Creating log directory..."
sudo mkdir -p "$LOG_DIR"
sudo touch "$LOG_DIR/eyeogotchi.log"
sudo chmod 666 "$LOG_DIR/eyeogotchi.log"

# ------------------------------------------------------------
# ALIASES
# ------------------------------------------------------------
echo "[3/6] Adding aliases to ~/.bashrc..."

# eyeogotchi CLI alias
if ! grep -q "alias eyeogotchi=" "$BASHRC"; then
    echo "alias eyeogotchi=\"python3 $EYE_DIR/cli/eyeogotchi.py\"" >> "$BASHRC"
    echo "Added alias: eyeogotchi"
else
    echo "Alias 'eyeogotchi' already exists."
fi

# config alias
if ! grep -q "alias config=" "$BASHRC"; then
    echo "alias config=\"sudo nano $EYE_DIR/config.yaml\"" >> "$BASHRC"
    echo "Added alias: config"
else
    echo "Alias 'config' already exists."
fi

# ------------------------------------------------------------
# SYSTEMD SERVICE
# ------------------------------------------------------------
echo "[4/6] Installing systemd service..."

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Eyeogotchi Runtime
After=network.target

[Service]
Type=simple
WorkingDirectory=$EYE_DIR
ExecStart=$VENV_DIR/bin/python3 eyeogotchi.py
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable eyeogotchi || true

echo "Systemd service installed at $SERVICE_FILE"

# ------------------------------------------------------------
# PERMISSIONS + ENVIRONMENT
# ------------------------------------------------------------
echo "[5/6] Ensuring permissions..."
sudo chown -R "$USER":"$USER" "$EYE_DIR"

# ------------------------------------------------------------
# FINISH
# ------------------------------------------------------------
echo "[6/6] Installation complete!"
echo ""
echo "Run this to activate aliases:"
echo "    source ~/.bashrc"
echo ""
echo "Start Eyeogotchi:"
echo "    sudo systemctl start eyeogotchi"
echo ""
echo "Open the Portal:"
echo "    http://localhost"
echo ""
echo "You're ready to go!"
