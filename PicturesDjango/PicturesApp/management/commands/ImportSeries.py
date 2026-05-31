from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction
from django.conf import settings
from pathlib import Path
import os
import hashlib


class Command(BaseCommand):
    help = (
        "High-level command to import a new photo series.\n\n"
        "It orchestrates the full import process in the correct and safe order:\n"
        "  1. Smart resizing (only processes what is needed)\n"
        "  2. If resizing succeeds completely → atomic creation of PhotoModel records + EXIF extraction\n\n"
        "This command is the recommended way to import series, whether from the web interface or from the command line.\n\n"
        "Example:\n"
        "    python manage.py ImportSeries \\\n"
        "        --jpegsdirectory '/home/mehdi/Images/scans/voyages/fuerteventura_2013' \\\n"
        "        --subject 'Voyage à Fuerteventura - 2013' \\\n"
        "        --date 'Été 2013' \\\n"
        "        --comment 'Superbe voyage aux Canaries avec les enfants.'"
    )

    def add_arguments(self, parser):
        parser.add_argument('--jpegsdirectory', type=str, required=True,
                            help='Full path to the folder containing the JPEGs (must be under scans/)')
        parser.add_argument('--subject', type=str, required=True,
                            help='Subject / title of the series (must be unique)')
        parser.add_argument('--date', type=str, required=True,
                            help='Date or period (free text)')
        parser.add_argument('--comment', type=str, required=True,
                            help='General comment about the series')

    def handle(self, *args, **options):
        jpegsdirectory = options['jpegsdirectory']
        subject = options['subject']
        date = options['date']
        comment = options['comment']

        self.stdout.write(self.style.MIGRATE_HEADING("=== Starting ImportSeries ==="))
        self.stdout.write(f"Subject : {subject}")
        self.stdout.write(f"Date    : {date}")
        self.stdout.write(f"Source  : {jpegsdirectory}")

        # Validate the directory using the same robust logic as elsewhere
        # (avoids the fragile startswith check we removed earlier)
        try:
            scans_root = (Path(settings.IMAGES_PATH) / "scans").resolve(strict=True)
            selected = Path(jpegsdirectory).expanduser().resolve(strict=True)
        except (FileNotFoundError, RuntimeError, OSError):
            raise CommandError("Le dossier spécifié n'existe pas ou n'est pas accessible.")

        if not selected.is_relative_to(scans_root):
            raise CommandError("Le dossier doit se trouver à l'intérieur du dossier 'scans/'.")

        if selected == scans_root:
            raise CommandError(
                "Vous devez sélectionner un sous-dossier à l'intérieur de 'scans/' "
                "(ex: scans/voyages/fuerteventura_2013), pas le dossier scans lui-même."
            )

        seriesdestdirectory = str(selected.relative_to(scans_root))

        try:
            # ============================================================
            # STEP 1: Smart resizing (always runs first, outside transaction)
            # ============================================================
            self.stdout.write(self.style.WARNING("\n[1/3] Smart resizing..."))
            call_command(
                'ResizeJpegs',
                seriesdestdirectory=seriesdestdirectory,
                verbosity=1
            )
            self.stdout.write(self.style.SUCCESS("Resizing completed successfully."))

            # ============================================================
            # STEP 2: Atomic DB operations (only if resizing succeeded)
            # ============================================================
            self.stdout.write(self.style.WARNING("\n[2/3] Creating database entries + extracting EXIF (transactional)..."))

            with transaction.atomic():
                # Create the PhotoModel entries
                call_command(
                    'PrepareEntreesJpegs',
                    jpegsdirectory=jpegsdirectory,
                    subject=subject,
                    date=date,
                    comment=comment,
                    verbosity=1
                )

                # Generate the checksum (MD5 of subject) and run EXIF extraction
                desiredsubjectMD5 = hashlib.md5(subject.encode(), usedforsecurity=False).hexdigest()
                call_command(
                    'ExtractEXIFInfos',
                    SubjectMD5=desiredsubjectMD5,
                    verbosity=1
                )

            self.stdout.write(self.style.SUCCESS("Database entries and EXIF extraction completed successfully (transaction committed)."))

            # Final success message
            self.stdout.write(self.style.SUCCESS("\n=== ImportSeries completed successfully ==="))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"\nImportSeries failed: {e}"))
            self.stderr.write(self.style.ERROR("No partial data was committed to the database (transaction rolled back if applicable)."))
            raise CommandError(f"Import failed: {e}")
