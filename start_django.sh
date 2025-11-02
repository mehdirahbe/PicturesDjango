#!/bin/bash

# Aller dans le répertoire du projet (optionnel si tu l'exécutes déjà depuis là, mais utile pour la portabilité)
cd "$(dirname "$0")"  # Ça place le script dans son propre répertoire

# Activer l'environnement virtuel
source .venv/bin/activate

cd PicturesDjango

# Lancer le serveur de développement
gunicorn PicturesDjango.wsgi:application --bind 0.0.0.0:8000 --reload --workers 3

