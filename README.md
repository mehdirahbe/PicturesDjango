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

Note on Pillow:
This project uses pillow-simd (in requirements.txt) instead of regular Pillow
for much faster JPEG resizing (very noticeable on Intel CPUs).
If you reinstall dependencies, make sure to use:
    pip uninstall pillow
    pip install pillow-simd
Do not have both installed at the same time.


Then:
```bash
source .venv/bin/activate
pip install -r requirements.txt
# En développement uniquement :
pip install -r requirements-dev.txt
```

If it fails with error: command 'x86_64-linux-gnu-gcc' failed: No such file or directory, install gcc:
```bash
sudo apt-get install python3-dev gcc
```

### Dépendances Python (`requirements.txt` / `requirements-dev.txt`)

Deux fichiers volontairement **séparés** :

| Fichier | Rôle |
|---------|------|
| `requirements.txt` | Runtime du site (Gunicorn, Django, Pillow-SIMD, etc.) |
| `requirements-dev.txt` | Outils de dev uniquement (`django-debug-toolbar`) |

**Workflow habituel** — ajout au fil de l'eau, puis freeze :

1. Installer dans le venv au besoin : `pip install MonPaquet`
2. Tester : `python manage.py test`
3. Figér les versions :
   ```bash
   pip freeze > requirements.txt
   ```
4. Relire le fichier : retirer de `requirements.txt` tout ce qui est purement dev (`django-debug-toolbar`, `pip-audit`, etc.) et le reporter dans `requirements-dev.txt`.

C'est la méthode utilisée sur ce projet : on installe au fur et à mesure, on freeze, puis on trie prod / dev. Pas besoin de tout écrire à la main.

**Variante** (sans freeze complet) : ajouter une seule ligne `MonPaquet==x.y.z` (`pip show MonPaquet` pour la version).

**Mise à jour de sécurité** (ex. Django) :

```bash
pip install --upgrade Django==6.0.7
pip freeze > requirements.txt   # puis re-trier prod / dev si besoin
python manage.py test
```

**Audit optionnel** (hors `requirements.txt`) :

```bash
pip install pip-audit
pip-audit
```

`pip-audit` reste dans le venv local ; ne pas le laisser dans `requirements.txt` après un freeze.

Once django is installed, you can create dummy project:
django-admin startproject PicturesDjango

Source will be in subdir. From there, crete the app:
python manage.py startapp PicturesApp

To run it in debug, it is:
python manage.py runserver

### Django Debug Toolbar (recommandé en développement)

Pour voir les requêtes SQL, les temps de rendu, les requêtes dupliquées (N+1), etc. :

1. Installe les dépendances (prod + dev) :
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
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

To run in local in release (script habituel, depuis la racine du dépôt) :
```bash
./start_django.sh
```
Écoute sur `0.0.0.0:8000` (localhost + Tailscale/LAN). Équivalent manuel :
```bash
gunicorn PicturesDjango.wsgi:application --bind 0.0.0.0:8000 --reload --timeout 600 --workers 1
```


For internationalisation:
1) Create .po files, you will have to add translations in them: (no need for english as text in html are already english):
python manage.py makemessages --locale fr

Note: you may need to do first:
sudo apt install gettext

2) Each time translations are added in po file(s), you have to compile them:
python manage.py compilemessages

To use from internet, use Tailscale Serve.
To enable https:
run once on the laptop:
sudo tailscale serve --bg --https=443 http://127.0.0.1:8000 

It give the url to use ptovided your are logged with same account.
In my case, https://mehdi-thinkbook-13s-g2-itl.taila97662.ts.net/ 

Do NOT activate Funnel or all internet will have access, need strong authentification on the website, which is not the case here.
