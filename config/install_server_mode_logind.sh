#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
sudo mkdir -p /etc/systemd/logind.conf.d
sudo cp "$SCRIPT_DIR/logind-server-mode.conf" /etc/systemd/logind.conf.d/server-mode.conf
sudo systemctl restart systemd-logind
echo "logind server-mode installé : /etc/systemd/logind.conf.d/server-mode.conf"