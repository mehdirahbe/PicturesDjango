#!/bin/bash
set -e  # Arrête le script si une commande échoue

echo "🚀 Déploiement PicturesDjango - Démarrage..."

# ===================== CONFIG =====================
PROJECT_DIR="PicturesDjango"
VENV=".venv"
SERVICE_NAME="picturesdjango-gunicorn"
REQUIREMENTS="requirements.txt"
# ================================================

# Se placer dans le répertoire du script
cd "$(dirname "$0")"

# ===================== GIT PULL =====================
echo "📥 Mise à jour du code depuis Git..."
git pull --ff-only   # --ff-only évite les merges automatiques risqués

# ===================== ENVIRONNEMENT VIRTUEL =====================
echo "🔧 Activation de l'environnement virtuel..."
source "$VENV/bin/activate"

# Mise à jour des dépendances
echo "📦 Installation/Mise à jour des dépendances Python..."
pip install --upgrade pip
pip install -r "$REQUIREMENTS"

cd "$PROJECT_DIR"

# ===================== DJANGO COMMANDS =====================
echo "🗄️  Migration de la base de données..."
python manage.py migrate --noinput

echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "🌐 Compilation des traductions..."
python manage.py compilemessages --ignore=.venv 2>/dev/null || true

# ===================== RESTART SERVICE =====================
echo "♻️  Redémarrage du service Gunicorn..."
sudo systemctl restart "$SERVICE_NAME"

echo "✅ Déploiement terminé avec succès !"
