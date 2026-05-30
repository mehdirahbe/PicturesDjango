# PicturesDjango


How to:
Change look: adapt CSS in base.html

For developpers, how to run site locally:
1) Install python, django and mandatory modules (see requirements.txt) 
2) Run python manage.py migrate (configure postgress db first, see settings.py)
3) Then python manage.py createsuperuser (optional)
4) Then python manage.py collectstatic
5) Check that all is fine: python manage.py test
6) Run the site with: python manage.py runserver

For venv,
python3 -m venv .venv
If it fails, run this first:
sudo apt install python3.10-venv

To update all:
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip list --outdated | grep -v '^\-e' | cut -d = -f1 | xargs -n1 pip install -U
pip freeze >requirements.txt

You may need the following packages:
sudo apt update
sudo apt install -y \
    build-essential \
    python3-dev \
    libjpeg-turbo8-dev \
    libpng-dev \
    zlib1g-dev \
    libwebp-dev \
    libtiff5-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev

-->pip list --outdated must return an empty list

Note on Pillow:
This project uses pillow-simd (in requirements.txt) instead of regular Pillow
for much faster JPEG resizing (very noticeable on Intel CPUs).
If you reinstall dependencies, make sure to use:
    pip uninstall pillow
    pip install pillow-simd
Do not have both installed at the same time.


Then:
source .venv/bin/activate
pip install -r requirements.txt

If it fails with error: command 'x86_64-linux-gnu-gcc' failed: No such file or directory, install gcc:
sudo apt-get install python3-dev
sudo apt-get install gcc


To generate an up to date requirements:
pip freeze > requirements.txt

To update all packages to the most recent version:
pip list --outdated --format json | jq '.[] | .name' | xargs -n1 pip install -U
You may need to install this:
sudo apt  install jq

Once django is installed, you can create dummy project:
django-admin startproject PicturesDjango

Source will be in subdir. From there, crete the app:
python manage.py startapp PicturesApp

To run it in debug, it is:
python manage.py runserver

### Django Debug Toolbar (recommandé en développement)

Pour voir les requêtes SQL, les temps de rendu, les requêtes dupliquées (N+1), etc. :

1. Installe les dépendances de développement :
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Assure-toi que `DEBUG=True` dans ton fichier `.env` (ou via la variable d'environnement).

3. Le toolbar apparaîtra automatiquement sur la droite de l'écran quand tu navigues sur le site en mode debug.

Le toolbar est **uniquement activé** quand `DEBUG=True` et n'est donc jamais présent en production.

Fichier `requirements-dev.txt` contient `django-debug-toolbar`. Ne l'ajoute pas dans `requirements.txt` (il est réservé au développement).

Créez un fichier nommé `.env` dans le répertoire racine du projet (à côté de manage.py).

Variables supportées dans le `.env` :

```env
IMAGES_PATH=/home/mehdi/Images
DEBUG=False                 # True seulement quand tu veux debugger
SECRET_KEY=                 # Optionnel pour un usage 100% local sur ton PC
```

Exemple minimal :
```
IMAGES_PATH=/home/mehdi/Images
```

To run in local in release:
gunicorn PicturesDjango.wsgi:application


For internationalisation:
1) Create .po files, you will have to add translations in them: (no need for english as text in html are already english):
python manage.py makemessages --locale fr

Note: you may need to do first:
sudo apt install gettext

2) Each time translations are added in po file(s), you have to compile them:
python manage.py compilemessages
