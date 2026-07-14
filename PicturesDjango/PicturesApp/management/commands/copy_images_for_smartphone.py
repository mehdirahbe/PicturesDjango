from django.core.management.base import BaseCommand
from django.conf import settings
from PicturesApp.PhotoModel import PhotoModel
import os
import shutil


class Command(BaseCommand):
    help = 'Copie les images pour le smartphone dans un nouveau répertoire'

    def handle(self, *args, **options):
        smartphone_dir = os.path.join(settings.IMAGES_PATH, 'smartphone')

        if not os.path.exists(smartphone_dir):
            os.makedirs(smartphone_dir)

        queryset = PhotoModel.objects.filter(
            premier_niveau__isnull=False,
            nom_fichier_jpeg__isnull=False,
            agrandi=True,
        )

        for photo in queryset.iterator():
            parts = [photo.premier_niveau, photo.second_niveau]
            if photo.troisieme_niveau:
                parts.append(photo.troisieme_niveau)

            source_path = os.path.join(settings.IMAGES_PATH, *parts, 'big', photo.nom_fichier_jpeg)
            dest_path = os.path.join(smartphone_dir, *parts, photo.nom_fichier_jpeg)

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            if not os.path.exists(dest_path):
                if os.path.exists(source_path):
                    shutil.copy2(source_path, dest_path)
                    self.stdout.write(self.style.SUCCESS(f'Copié: {source_path} -> {dest_path}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Fichier non trouvé: {source_path}'))

        self.stdout.write(self.style.SUCCESS('Copie des images terminée.'))