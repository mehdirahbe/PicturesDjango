#!/bin/bash

# Aller dans le répertoire du projet (optionnel si tu l'exécutes déjà depuis là, mais utile pour la portabilité)
cd "$(dirname "$0")"  # Ça place le script dans son propre répertoire

# clean residues from previous run
pkill -9 -f gunicorn

# Activer l'environnement virtuel
source .venv/bin/activate

cd PicturesDjango

# Écoute sur toutes les interfaces (0.0.0.0:8000) :
# - local : http://127.0.0.1:8000
# - Tailscale / LAN : http://100.x.x.x:8000
# HTTPS smartphone : tailscale serve → http://127.0.0.1:8000 (une fois : voir README)
# 1 worker : SQLite ne gère pas bien les écritures concurrentes entre processus.
echo "Gunicorn → 0.0.0.0:8000 (Ctrl+C pour arrêter)"
gunicorn PicturesDjango.wsgi:application --bind 0.0.0.0:8000 --reload --timeout 600 --workers 1


