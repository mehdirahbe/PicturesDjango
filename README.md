# PicturesDjango


How to:
1) To add a new link, you have to adapt urls.py, views.py (to serve it) and carstatus.html (to display the link). See for example sentry or door lock.

2) If you want to display an additional information on the car, you probably only have to adapt carstatus.html, except if it is a computed value (such as battery degradattion) where you will also have to adapt views.py to compute the value and put it in the context passed to rendering.

3) Change look: adapt CSS in base.html

For developpers, how to run site locally:
1) Install python, django and mandatory modules (see requirements.txt) 
2) Run python3 manage.py migrate (configure postgress db first, see settings.py)
3) Then python3 manage.py createsuperuser (optional)
4) Then python3 manage.py collectstatic
5) Check that all is fine: python3 manage.py test
6) Run the site with: python3 manage.py runserver

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

To run it, it is:
python manage.py