from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from PicturesApp.PhotoModel import PhotoModel
from PIL import Image, ImageStat
from pathlib import Path
import os


def analyze_exposure(image_path: Path | str, max_size: int = 800):
    """
    Analyse l'exposition d'une image JPEG de manière légère et rapide.

    - Downscale à max_size (800px) pour que l'analyse reste instantanée même
      sur de gros scans originaux.
    - Retourne luminance moyenne (0-255) + pourcentages de pixels "clipés"
      dans les ombres (0-10) et les hautes lumières (245-255).

    Utilise uniquement Pillow (pas de numpy/OpenCV).
    """
    try:
        p = Path(image_path)
        if not p.exists():
            return None

        with Image.open(p) as img:
            # Downscale pour la vitesse (l'exposition ne nécessite pas la pleine résolution)
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.LANCZOS)

            gray = img.convert('L')

            # Luminance moyenne
            stat = ImageStat.Stat(gray)
            luminance_mean = stat.mean[0]

            # Histogramme pour les zones extrêmes
            hist = gray.histogram()
            total = sum(hist)
            if total == 0:
                return None

            # Pixels très sombres (0-10) et très clairs (245-255)
            shadow = sum(hist[0:11])
            highlight = sum(hist[245:256])

            shadow_pct = (shadow / total) * 100.0
            highlight_pct = (highlight / total) * 100.0

            return {
                'luminance_mean': round(luminance_mean, 1),
                'shadow_clip_pct': round(shadow_pct, 2),
                'highlight_clip_pct': round(highlight_pct, 2),
            }
    except Exception:
        return None


def _build_photo_path(photo, images_root: Path) -> Path | None:
    """
    Reconstruit le chemin vers le gros JPEG (privilégie 'big' si présent,
    sinon retombe sur le fichier dans scans/ pour les anciens imports).
    """
    if not photo.nom_fichier_jpeg:
        return None

    # 1) Essayer d'abord la version "big" (la plus grande disponible)
    base = images_root / photo.premier_niveau / photo.second_niveau
    if photo.troisieme_niveau:
        base = base / photo.troisieme_niveau

    big_path = base / 'big' / photo.nom_fichier_jpeg
    if big_path.exists():
        return big_path

    # 2) Fallback : l'original dans scans/ (utile juste après import avant resize)
    scans_path = images_root / 'scans' / photo.premier_niveau / photo.second_niveau
    if photo.troisieme_niveau:
        scans_path = scans_path / photo.troisieme_niveau
    scans_jpeg = scans_path / photo.nom_fichier_jpeg
    if scans_jpeg.exists():
        return scans_jpeg

    return None


class Command(BaseCommand):
    help = (
        "Analyse l'exposition des photos d'une série (ou de toute la base) "
        "et stocke les métriques de luminance / clipping.\n\n"
        "Usage:\n"
        "  python manage.py AnalyzePhotoQuality --SubjectMD5 <md5>\n"
        "  python manage.py AnalyzePhotoQuality                 # toute la base (lent)\n\n"
        "Les métriques permettent ensuite d'afficher dans la planche contacts "
        "le top 5 des images à améliorer (trop sombres ou trop claires)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--SubjectMD5',
            type=str,
            default=None,
            help='MD5 du sujet. Si absent, analyse toutes les photos (lent sur grosse collection).'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Ré-analyser même les photos déjà traitées.'
        )

    def handle(self, *args, **options):
        subject_md5 = options.get('SubjectMD5')
        force = options.get('force', False)

        images_root = Path(settings.IMAGES_PATH)

        if subject_md5:
            qs = PhotoModel.objects.filter(
                checksum=subject_md5,
                agrandi=True,
                nom_fichier_jpeg__isnull=False
            ).exclude(nom_fichier_jpeg='')
            self.stdout.write(f"Mode série unique (MD5={subject_md5})")
        else:
            qs = PhotoModel.objects.filter(
                agrandi=True,
                nom_fichier_jpeg__isnull=False
            ).exclude(nom_fichier_jpeg='')
            self.stdout.write("ATTENTION : mode TOUTE LA BASE (peut être long)")
            self.stdout.write("Appuyez sur Ctrl+C pour annuler si nécessaire.")

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("Aucune photo à analyser."))
            return

        self.stdout.write(f"{total} photos candidates.\n")

        updated = 0
        skipped = 0
        errors = 0

        for idx, photo in enumerate(qs.iterator(), 1):
            # Skip si déjà analysé (sauf --force)
            if not force and photo.quality_analyzed_at is not None:
                skipped += 1
                if idx % 50 == 0:
                    self.stdout.write(f"  [{idx}/{total}] ... (skip déjà analysées)")
                continue

            photo_path = _build_photo_path(photo, images_root)
            if not photo_path:
                errors += 1
                continue

            metrics = analyze_exposure(photo_path)
            if metrics is None:
                errors += 1
                continue

            photo.luminance_mean = metrics['luminance_mean']
            photo.shadow_clip_pct = metrics['shadow_clip_pct']
            photo.highlight_clip_pct = metrics['highlight_clip_pct']
            photo.quality_analyzed_at = timezone.now()
            photo.save(update_fields=[
                'luminance_mean', 'shadow_clip_pct',
                'highlight_clip_pct', 'quality_analyzed_at'
            ])
            updated += 1

            if idx % 20 == 0 or idx == total:
                self.stdout.write(
                    f"  [{idx}/{total}] mis à jour: {updated} | erreurs: {errors}"
                )

        self.stdout.write(self.style.SUCCESS(
            f"\nTerminé. {updated} photos analysées/mises à jour, "
            f"{skipped} ignorées (déjà analysées), {errors} erreurs."
        ))
