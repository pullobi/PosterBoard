#!/bin/bash


SERVICE_NAME="run_script"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SCRIPT_DIR="$(pwd)"
RUN_SCRIPT="${SCRIPT_DIR}/run.sh"
USER_NAME=$(whoami)


if [[ ! -f "$RUN_SCRIPT" ]]; then
    echo "Error: run.sh not found in the current directory ($SCRIPT_DIR)."
    exit 1
fi


echo "Adding message announcement to run.sh..."
sed -i '1i echo "Service is starting: $(date)" | wall' "$RUN_SCRIPT"


echo "Creating systemd service file at $SERVICE_FILE..."
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Run Script on Startup
After=network.target

[Service]
ExecStart=${RUN_SCRIPT}
WorkingDirectory=${SCRIPT_DIR}
Restart=always
User=${USER_NAME}
Group=${USER_NAME}

[Install]
WantedBy=multi-user.target
EOL


echo "Making run.sh executable..."
chmod +x "$RUN_SCRIPT"


echo "Reloading systemd, enabling, and starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl start "${SERVICE_NAME}.service"


echo "Service created and started. Checking status..."
sudo systemctl status "${SERVICE_NAME}.service"

echo "Done. The service will now announce messages and run run.sh on startup."