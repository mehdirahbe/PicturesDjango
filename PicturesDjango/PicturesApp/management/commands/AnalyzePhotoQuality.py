from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_lazy as _lazy
from PicturesApp.PhotoModel import PhotoModel
from PIL import Image, ImageStat
from pathlib import Path
import os


def analyze_exposure(image_path: Path | str, max_size: int = 600):
    """
    Analyze the exposure of a JPEG image in a lightweight way.

    - Downscales to max_size for fast analysis even on large original scans.
    - Returns mean luminance (0-255) + percentages of clipped pixels
      in shadows (0-10) and highlights (245-255).

    Uses only Pillow (no numpy/OpenCV).
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
    Rebuilds the path to a JPEG for exposure analysis.
    Prefers the smallest available versions (contactsheet > view > big)
    because high resolution is unnecessary for luminance + histogram analysis.
    """
    if not photo.nom_fichier_jpeg:
        return None

    base = images_root / photo.premier_niveau / photo.second_niveau
    if photo.troisieme_niveau:
        base = base / photo.troisieme_niveau

    # Ordre de préférence : du plus petit au plus gros (pour la vitesse)
    for size_dir in ("contactsheet", "view", "big"):
        candidate = base / size_dir / photo.nom_fichier_jpeg
        if candidate.exists():
            return candidate

    # Dernier recours : l'original dans scans/ (cas d'import très récent)
    scans_path = images_root / "scans" / photo.premier_niveau / photo.second_niveau
    if photo.troisieme_niveau:
        scans_path = scans_path / photo.troisieme_niveau
    scans_jpeg = scans_path / photo.nom_fichier_jpeg
    if scans_jpeg.exists():
        return scans_jpeg

    return None


class Command(BaseCommand):
    help = _lazy(
        "Analyze photo exposure of a series (or the whole database) "
        "and store luminance/clipping metrics.\n\n"
        "Usage:\n"
        "  python manage.py AnalyzePhotoQuality --SubjectMD5 <md5>\n"
        "  python manage.py AnalyzePhotoQuality                 # full database (slow)\n\n"
        "The metrics are then used to display the top 5 images to improve "
        "(too dark or too bright) in the contact sheet."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--SubjectMD5',
            type=str,
            default=None,
            help=_lazy('MD5 of the subject. If omitted, analyzes all photos (slow on large collections).')
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help=_lazy('Re-analyze even photos that were already processed.')
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
            self.stdout.write(_("WARNING: Full database mode (can be slow)"))
            self.stdout.write(_("Press Ctrl+C to cancel if needed."))

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING(_("No photos to analyze.")))
            return

        self.stdout.write(f"{total} photos candidates.\n")

        updated = 0
        skipped = 0
        errors = 0

        for idx, photo in enumerate(qs.iterator(), 1):
            # Skip if already analyzed (unless --force)
            if not force and photo.quality_analyzed_at is not None:
                skipped += 1
                if idx % 50 == 0:
                    self.stdout.write(_("  [{}/{}] ... (skip already analyzed)").format(idx, total))
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
                    _("  [{}/{}] updated: {} | errors: {}").format(idx, total, updated, errors)
                )

        self.stdout.write(self.style.SUCCESS(
            _("\nDone. {} photos analyzed/updated, {} skipped (already analyzed), {} errors."
            ).format(updated, skipped, errors)
        ))
