#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_NAME="picturesdjango-gunicorn.service"

sudo cp "$SCRIPT_DIR/picturesdjango-gunicorn.service" "/etc/systemd/system/$SERVICE_NAME"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "Service installé et démarré : $SERVICE_NAME"
echo "  statut : systemctl status $SERVICE_NAME"
echo "  arrêt (avant runserver) : sudo systemctl stop $SERVICE_NAME"
echo "  désactiver au boot : sudo systemctl disable $SERVICE_NAME"