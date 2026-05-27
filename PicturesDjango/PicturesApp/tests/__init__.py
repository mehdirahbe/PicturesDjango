# Tests package for PicturesApp
# 
# Stratégie globale de tests :
# - Pas d'accès aux vraies photos ni à la vraie base de données en production.
# - Utilisation de SQLite en mémoire pour les tests qui ont besoin de DB.
# - Mocking intensif pour tout ce qui touche au filesystem (IMAGES_PATH).
# - Focus sur la robustesse des entrées utilisateur (surtout les formulaires).
