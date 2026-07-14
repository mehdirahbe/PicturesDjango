#!/bin/bash

# Aller dans le répertoire du projet (optionnel si tu l'exécutes déjà depuis là, mais utile pour la portabilité)
cd "$(dirname "$0")"  # Ça place le script dans son propre répertoire

# clean residues from previous run
pkill -9 -f gunicorn

# Activer l'environnement virtuel
source .venv/bin/activate

cd PicturesDjango

# Lancer le serveur de développement
# 1 worker: SQLite does not handle concurrent writes well across processes.
gunicorn PicturesDjango.wsgi:application --bind 0.0.0.0:8000 --reload --timeout 600 --workers 1


