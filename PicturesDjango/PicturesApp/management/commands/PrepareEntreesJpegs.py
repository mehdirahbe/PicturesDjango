import os
from django.core.management.base import BaseCommand
from PicturesApp.PhotoModel import PhotoModel
from PicturesDjango import settings


def process_images(dias_dir, jpeg_dir,subject, date, commentaire):
    scans_dir = os.path.join(dias_dir, 'scans')

    if not jpeg_dir.startswith(scans_dir):
        raise ValueError("Le dossier sélectionné doit être dans le sous-répertoire 'scans' du répertoire 'dias'")

    # Extraire les niveaux de répertoires
    relative_path = jpeg_dir[len(scans_dir):].lstrip(os.sep)
    dir_parts = relative_path.split(os.sep)
    if len(dir_parts) > 3:
        raise ValueError("Le niveau max de sous-répertoires est de trois")

    # Lister et trier les fichiers JPG
    jpg_files = []
    for root, _, files in os.walk(jpeg_dir):
        for file in files:
            if file.lower().endswith('.jpg'):
                jpg_files.append(file)

    # Trier les fichiers par nom
    jpg_files.sort()

    for file in jpg_files:
        # Créer un nouveau record
        photo = PhotoModel(
            sujet=subject,
            date=date,
            boite='',  # À compléter si nécessaire
            rangee=None,  # À compléter si nécessaire
            numero=None,  # À compléter si nécessaire
            sujet_dias='',  # ou un commentaire spécifique
            agrandi=True,
            classe=False,  # À compléter si nécessaire
            verifie=False,  # À compléter si nécessaire
            commentaire=commentaire,
            camera_digitale=True,
            premier_niveau=dir_parts[0] if len(dir_parts) > 0 else '',
            second_niveau=dir_parts[1] if len(dir_parts) > 1 else '',
            troisieme_niveau=dir_parts[2] if len(dir_parts) > 2 else '',
            nom_fichier_jpeg=file
        )
        photo.save()

class Command(BaseCommand):
    help = (
        'Prepare records from a serie of jpg image located in a subdir of scan'
        "So syntax is python manage.py PrepareEntreesJpegs --jpegsdirectory '/home/mehdi/Images/scans/Corentin/2015' --subject 'Photos de Corentin en 2015 (5 ans)' --date 'Année 2015' --comment 'Aquarium, animations en bougeant un objet sur le fauteuil'" )

    def add_arguments(self, parser):
        parser.add_argument('--jpegsdirectory', type=str,
                            help='Required, where are the jpegs, ie /home/mehdi/Images/scans/voyages/amsterdam_TreldeNaes_Hoganas_2024')
        parser.add_argument('--subject', type=str,
                            help='Required, subject ie Vacances en Bretagne (5 au 11 aout 2024), it cannot already exists!')
        parser.add_argument('--date', type=str, help='Required, date or date range, ie aout 2024')
        parser.add_argument('--comment', type=str,
                            help='Required, generic comment of the pictures serie, provide additional information on places visited, persons,...')

    def handle(self, *args, **options):
        dias_dir = settings.IMAGES_PATH

        jpeg_dir = options["jpegsdirectory"]
        if jpeg_dir is None:
            print("Required arg jpegsdirectory missing")
            return

        subject = options["subject"]
        if subject is None:
            print("Required arg subject missing")
            return

        date = options["date"]
        if date is None:
            print("Required args date missing")
            return

        commentaire = options["comment"]
        if commentaire is None:
            print("Required args comment missing")
            return

        print("Will run PrepareEntreesJpegs")
        print("jpeg_dir is: "+jpeg_dir)
        print("subject is: " + subject)
        print("date is: " + date)
        print("commentaire is: " + commentaire)

        #uncomment for a dry run
        #return

        process_images(dias_dir,jpeg_dir, subject, date, commentaire)
        return


