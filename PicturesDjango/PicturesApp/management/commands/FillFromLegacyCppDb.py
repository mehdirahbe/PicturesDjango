import struct

from django.db import models
from django.core.management.base import BaseCommand

from  PicturesApp.PhotoModel import PhotoModel

def read_null_terminated_string(f, encoding='ISO-8859-1'):
    chars = []
    while True:
        char = f.read(1)
        if char == b'\x00' or char == b'':
            break
        chars.append(char)
    return b''.join(chars).decode(encoding)

def read_binaire_file(filename):
    with open(filename, 'rb') as f:
        # Lire la version (4 octets) et le nombre de records (4 octets)
        version, num_records = struct.unpack('II', f.read(8))

        photos = []

        for _ in range(num_records):
            # Lire les chaînes de caractères de longueur variable
            sujet = read_null_terminated_string(f)
            date = read_null_terminated_string(f)
            boite = read_null_terminated_string(f)

            # Lire les entiers non signés (rangee et numero)
            rangee, numero = struct.unpack('II', f.read(8))

            # Lire les autres chaînes de caractères
            sujet_dias = read_null_terminated_string(f)

            # Lire les BOOL (4 octets chacun)
            agrandi, classe, verifie = struct.unpack('III', f.read(12))

            # Lire le commentaire et les niveaux de répertoire
            commentaire = read_null_terminated_string(f)
            camera_digitale = struct.unpack('I', f.read(4))[0]
            premier_niveau = read_null_terminated_string(f)
            second_niveau = read_null_terminated_string(f)
            troisieme_niveau = read_null_terminated_string(f)
            nom_fichier_jpeg = read_null_terminated_string(f)

            # Préparer le dictionnaire des données
            photo_data = {
                'sujet': sujet[:100],
                'date': date[:100],
                'boite': boite[:10],
                'rangee': rangee,
                'numero': numero,
                'sujet_dias': sujet_dias,
                'agrandi': bool(agrandi),
                'classe': bool(classe),
                'verifie': bool(verifie),
                'commentaire': commentaire,
                'camera_digitale': bool(camera_digitale),
                'premier_niveau': premier_niveau[:100],
                'second_niveau': second_niveau[:100],
                'troisieme_niveau': troisieme_niveau[:100],
                'nom_fichier_jpeg': nom_fichier_jpeg[:100],
            }

            # Ajouter à la liste des photos
            photos.append(photo_data)

        return photos


def save_photos_to_db(photos):
    for photo_data in photos:
        photo = PhotoModel(**photo_data)
        photo.save()

class Command(BaseCommand):
    help = (
        'Convert my very legacy format from the nineties where db was composed of nul terminated C strings, '
        'in western european.'
        'Need the db file, ie  /home/mehdi/Images/dbase/SQLBASE/Dias.bdd'
        'So syntax is python manage.py FillFromLegacyCppDb --DiasbddPath /home/mehdi/Images/dbase/SQLBASE/Dias.bdd')


    def add_arguments(self, parser):
        parser.add_argument('--DiasbddPath', type=str, help='Required, ie /home/mehdi/Images/dbase/SQLBASE/Dias.bdd')

    def handle(self, *args, **options):
        filename = options["DiasbddPath"]
        photos = read_binaire_file(filename)
        save_photos_to_db(photos)
        return
