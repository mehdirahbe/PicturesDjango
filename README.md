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

Images path can be precised like this:
Créez un fichier nommé .env dans le répertoire racine de votre projet Django, à côté de manage.py. Le contenu de ce fichier sera :
IMAGES_PATH=/home/mehdi/Images

To run in local in release:
gunicorn PicturesDjango.wsgi:application


For internationalisation:
1) Create .po files, you will have to add translations in them: (no need for english as text in html are already english):
python manage.py makemessages --locale fr

Note: you may need to do first:
sudo apt install gettext

2) Each time translations are added in po file(s), you have to compile them:
python manage.py compilemessages