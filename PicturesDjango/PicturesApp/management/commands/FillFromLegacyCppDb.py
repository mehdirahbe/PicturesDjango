import struct
import os
from django.core.management.base import BaseCommand
from PicturesApp.PhotoModel import PhotoModel

'''Import old db
Nightmarres found:
i) in some cases, there is a jpeg but file name is not set, it must be completed in an incremental way when agrandi is true,
starting at 001.jpg, with this formatting nom_fichier_jpeg = f"{the_number:03d}.jpg"
2) in some cases,  directories are not given. What we have is a batch named preparehtml.bat which internally reference the subject.
So by having batch location for a given subject, we can find the directories.
3) agrandi can very well means paper version, but not necessarily a jpeg version. So if camera_digitale is not set, the batch
presence is requiered to be sure that pictures does indeed really exists.
'''


def scan_for_batches(root_dir):
    subject_to_paths = {}
    current_jpeg_count = {}

    def recursive_scan(path, levels):
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            if os.path.isdir(entry_path):
                if levels < 3:
                    recursive_scan(entry_path, levels + 1)
            elif entry == 'preparehtml.bat':
                with open(entry_path, 'r', encoding='cp1252') as file:
                    for line in file:
                        if 'prephtml' in line:
                            subject = line.split('"')[1].lower()
                            relative_path = os.path.relpath(path, root_dir)
                            folders = relative_path.split(os.sep)
                            subject_to_paths[subject] = {
                                'premier_niveau': folders[0] if len(folders) > 0 else '',
                                'second_niveau': folders[1] if len(folders) > 1 else '',
                                'troisieme_niveau': folders[2] if len(folders) > 2 else ''
                            }
                            current_jpeg_count[subject] = 1

    recursive_scan(root_dir, 0)
    return subject_to_paths, current_jpeg_count


def read_null_terminated_string(f, encoding='ISO-8859-1'):
    chars = []
    while True:
        char = f.read(1)
        if char == b'\x00' or char == b'':
            break
        chars.append(char)
    return b''.join(chars).decode(encoding)


def read_binaire_file(filename):
    #load the batches to have the relation between subject and directories where pictures are located
    root_dir = '/home/mehdi/Images'
    subject_paths, jpeg_count = scan_for_batches(root_dir)

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

            #fill missing directories and jpeg name, see comment at top of this file
            if not nom_fichier_jpeg and agrandi:
                if sujet.lower() in subject_paths:
                    nom_fichier_jpeg = f"{jpeg_count[sujet.lower()]:03d}.jpg"
                    jpeg_count[sujet.lower()] = jpeg_count[sujet.lower()] + 1
                    if not premier_niveau:
                        premier_niveau = subject_paths[sujet.lower()]['premier_niveau']
                        second_niveau = subject_paths[sujet.lower()]['second_niveau']
                        troisième_niveau = subject_paths[sujet.lower()]['troisieme_niveau']

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
