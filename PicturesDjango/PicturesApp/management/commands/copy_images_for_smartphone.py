from django.core.management.base import BaseCommand
from django.conf import settings
from PicturesApp.PhotoModel import PhotoModel
import os
import shutil


class Command(BaseCommand):
    help = 'Copie les images pour le smartphone dans un nouveau répertoire'

    def handle(self, *args, **options):
        # Chemin vers le nouveau répertoire
        smartphone_dir = os.path.join(settings.IMAGES_PATH, 'smartphone')

        # Créer le répertoire si il n'existe pas
        if not os.path.exists(smartphone_dir):
            os.makedirs(smartphone_dir)

        # Parcourir tous les objets PhotoModel
        for photo in PhotoModel.objects.filter(
                premier_niveau__isnull=False,
                nom_fichier_jpeg__isnull=False
        ):
            # Construire le chemin source
            source_path = os.path.join(
                settings.IMAGES_PATH,
                photo.premier_niveau,
                photo.second_niveau,
                photo.troisieme_niveau or '',
                'big',
                photo.nom_fichier_jpeg
            )

            # Construire le chemin de destination
            dest_path = os.path.join(
                smartphone_dir,
                photo.premier_niveau,
                photo.second_niveau,
                photo.troisieme_niveau or '',
                photo.nom_fichier_jpeg
            )

            # Créer les répertoires nécessaires
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Copier le fichier
            if not os.path.exists(dest_path):
                if os.path.exists(source_path):
                    shutil.copy2(source_path, dest_path)
                    self.stdout.write(self.style.SUCCESS(f'Copié: {source_path} -> {dest_path}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Fichier non trouvé: {source_path}'))

        self.stdout.write(self.style.SUCCESS('Copie des images terminée.'))