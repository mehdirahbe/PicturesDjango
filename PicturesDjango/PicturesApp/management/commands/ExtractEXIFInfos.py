import struct
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from PIL import Image
from PIL.ExifTags import TAGS
import requests
from PicturesApp.PhotoModel import PhotoModel
from django.db.models import Q

from PicturesDjango import settings


def get_exif_data(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = {
                TAGS[key]: value
                for key, value in img._getexif().items()
                if key in TAGS
            }
        return exif_data
    except:
        return None


def extract_date(exif_data):
    if exif_data is not None and 'DateTimeOriginal' in exif_data:
        date_str = exif_data['DateTimeOriginal']
        date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        return date
    return None


def get_gps_coordinates(exif_data):
    if 'GPSInfo' in exif_data:
        gps_info = exif_data['GPSInfo']
        lat = gps_info.get(2, ())
        lon = gps_info.get(4, ())
        if lat and lon:
            lat_ref = gps_info.get(1, 'N')
            lon_ref = gps_info.get(3, 'E')
            lat = convert_to_degrees(lat)
            lon = convert_to_degrees(lon)
            if lat_ref == 'S':
                lat = -lat
            if lon_ref == 'W':
                lon = -lon
            return lat, lon
    return None, None


def convert_to_degrees(value):
    d = value[0]
    m = value[1]
    s = value[2]
    return d + (m / 60.0) + (s / 3600.0)


def gps_to_address(lat, lon):
    url = f'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}&zoom=12&language=fr'
    headers = {'User-Agent': 'PicturesDjango/1.0', 'Accept-L': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'}
    try:
        response = requests.get(url, headers=headers).json()
        if response:
            address = response.get('address')
            town = address["town"]
            country = address["country"]

            if town is not None and country is not None:
                return town + " (" + country + ")"
            else:
                if town is not None:
                    return town
        return None
    except:
        return None


class Command(BaseCommand):
    help = (
        'Extract EXIF infos from the picture when present'
        'So syntax is python manage.py ExtractEXIFInfos --todo: will see later for the args')

    def add_arguments(self, parser):
        parser.add_argument('--todo', type=str, help='Required, todo')

    def handle(self, *args, **options):
        #loop on all images having a jpeg (or which should have one)
        dias_dir = settings.IMAGES_PATH
        allphotos = PhotoModel.objects.filter(Q(premier_niveau__isnull=False) & ~Q(premier_niveau='')).filter(agrandi=True)  # Many records

        for photo in allphotos:
            try:
                # Image path
                photo_path = os.path.join(dias_dir,"scans",photo.premier_niveau,photo.second_niveau)
                if photo.troisieme_niveau:
                    photo_path = os.path.join(str(photo_path), photo.troisieme_niveau)
                photo_path = os.path.join(str(photo_path), photo.nom_fichier_jpeg)

                recUpdated=False
                exif = get_exif_data(photo_path)
                if exif is not None:
                    date = extract_date(exif)
                    if date is not None:
                        date_formatee = date.strftime('%d/%m/%Y')
                        if photo.date != date_formatee:
                            photo.date=date_formatee
                            recUpdated = True
                    '''if not photo.sujet_dias:
                        lat, lon = get_gps_coordinates(exif)
                        address = None
                        if not (lat is None or lon is None):
                            print(lat, lon)
                            address = gps_to_address(lat, lon)
                            if address is not None:
                                photo.sujet_dias = address
                                recUpdated = True'''

                # Sauvegarder le modèle
                if recUpdated:
                    photo.save()

            except Exception as e:
                print(f"Erreur lors du traitement de l'image {photo.image}: {e}")

        return

'''For gps, oops, I made a mistake:
Respecter la Limite de 1 Requête par Seconde : La politique d'utilisation de Nominatim recommande explicitement de ne pas dépasser 1 requête par seconde. Cela signifie que vous devez intégrer un délai d'au moins 1 seconde entre chaque appel à l'API.
import time 
time.sleep(1)

Limitation Journalière : Si vous avez beaucoup de requêtes à faire, envisagez de limiter le nombre de requêtes par jour. Par exemple, vous pourriez vous fixer un quota de 1000 requêtes par jour. Voici comment vous pourriez le gérer :
'''