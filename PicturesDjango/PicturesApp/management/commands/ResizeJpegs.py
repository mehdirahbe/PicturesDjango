from django.core.management.base import BaseCommand
import os
from PIL import Image, ExifTags
from django.conf import settings


def get_image_orientation(img):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            return exif[orientation]
    except (AttributeError, KeyError, IndexError):
        return None
    return None


def apply_orientation(img):
    orientation = get_image_orientation(img)
    if orientation is None:
        return img

    rotate_values = {
        2: Image.FLIP_LEFT_RIGHT,
        3: 180,
        4: Image.FLIP_TOP_BOTTOM,
        5: (Image.FLIP_LEFT_RIGHT, 90),
        6: 270,
        7: (Image.FLIP_LEFT_RIGHT, 270),
        8: 90,
    }

    if orientation in rotate_values:
        if isinstance(rotate_values[orientation], tuple):
            img = img.transpose(rotate_values[orientation][0])
            img = img.rotate(rotate_values[orientation][1], expand=True)
        elif isinstance(rotate_values[orientation], int):
            img = img.rotate(rotate_values[orientation], expand=True)
        else:
            img = img.transpose(rotate_values[orientation])

    return img


def resize_to_max_side(img, max_side, resample=None):
    """Resize preserving aspect ratio so the longest side is at most max_side."""
    if resample is None:
        resample = LANCZOS
    if img.width <= max_side and img.height <= max_side:
        return img.copy()
    if img.width >= img.height:
        new_width = max_side
        new_height = int(img.height * (max_side / img.width))
    else:
        new_height = max_side
        new_width = int(img.width * (max_side / img.height))
    return img.resize((new_width, new_height), resample)


# Compatibility shim for older Pillow versions
try:
    LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    LANCZOS = Image.LANCZOS  # Pillow < 9.1


def process_one_image(src_path, big_path, view_path, contact_path, max_big_size=1935):
    """
    Progressive resizing:
      - big        ← from original (LANCZOS)
      - view       ← from big        (LANCZOS)
      - contactsheet ← from view     (LANCZOS)
    All JPEG qualities ≥ 85.
    """
    try:
        with Image.open(src_path) as src:
            src = apply_orientation(src)
            # Ensure we are in a mode safe for JPEG
            if src.mode in ("RGBA", "P"):
                src = src.convert("RGB")
            else:
                src = src.convert("RGB")

            # 1. Big (highest quality)
            big_img = resize_to_max_side(src, max_big_size, LANCZOS)
            big_img.save(big_path, "JPEG", quality=93, optimize=True)

            # 2. View - from the big version we just created (in memory)
            view_img = resize_to_max_side(big_img, max_big_size // 2, LANCZOS)
            view_img.save(view_path, "JPEG", quality=89, optimize=True)

            # 3. Contactsheet - from the view version (in memory)
            contact_img = resize_to_max_side(view_img, max_big_size // 10, LANCZOS)
            contact_img.save(contact_path, "JPEG", quality=87, optimize=True)

    except Exception as e:
        print(f"Error processing {src_path}: {e}")
        raise





class Command(BaseCommand):
    help = (
        'Resize JPEG files to 3 sizes (big/view/contactsheet) using progressive downsampling.\n\n'
        'Key improvements:\n'
        '  - Progressive resizing (each size is generated from the immediately larger one)\n'
        '  - High quality LANCZOS only (no bilinear)\n'
        '  - JPEG quality never below 85\n'
        '  - Parallel processing\n\n'
        'Strongly recommended: install pillow-simd for much faster resizing on Intel CPUs:\n'
        '    pip install --upgrade --force-reinstall pillow-simd\n\n'
        'Example:\n'
        '    python manage.py ResizeJpegs --seriesdestdirectory=Corentin/2019'
    )

    def add_arguments(self, parser):
        parser.add_argument('--seriesdestdirectory', type=str, help='Required, ie voyages/amsterdam_TreldeNaes_Hoganas_2024')

    def handle(self, *args, **options):
        print(options)
        l_b_from300d = True

        sz_scanned_tifs_dir = None
        sz_dias_root_dir = settings.IMAGES_PATH
        sz_series_dest_dir = options['seriesdestdirectory']
        if sz_dias_root_dir is None or sz_series_dest_dir is None:
            print("Required args missing")
            return

        l_sz_root_serie = os.path.join(sz_dias_root_dir, sz_series_dest_dir)
        l_sz_big = os.path.join(l_sz_root_serie, "big")
        l_sz_contact_sheet = os.path.join(l_sz_root_serie, "contactsheet")
        l_sz_view = os.path.join(l_sz_root_serie, "view")
        l_sz_jpg_scans = os.path.join(sz_dias_root_dir, "scans", sz_series_dest_dir)

        print("Will run ResizeJpegs")
        print("l_sz_root_serie is: "+l_sz_root_serie)
        print("l_sz_big is: " + l_sz_big)
        print("l_sz_contact_sheet is: " + l_sz_contact_sheet)
        print("l_sz_view is: " + l_sz_view)
        print("l_sz_jpg_scans is: " + l_sz_jpg_scans)

        # Pillow acceleration info
        import PIL
        pil_version = getattr(PIL, '__version__', 'unknown')
        print(f"Pillow version: {pil_version}")

        if "post" in pil_version.lower():
            print("✓ Running with pillow-simd acceleration (good!)")
        else:
            print("! Running with standard Pillow. For much faster resizing on Intel CPUs, install pillow-simd instead.")

        #uncomment for a dry run
        #return

        os.makedirs(l_sz_root_serie, exist_ok=True)
        os.makedirs(l_sz_big, exist_ok=True)
        os.makedirs(l_sz_contact_sheet, exist_ok=True)
        os.makedirs(l_sz_view, exist_ok=True)
        os.makedirs(l_sz_jpg_scans, exist_ok=True)

        # --- Parallel progressive resizing ---
        import concurrent.futures
        from pathlib import Path

        # === Règle de conception ===
        # ResizeJpegs ne traite que les fichiers directement présents dans le dossier
        # de la série. Les sous-dossiers (raw, etc.) sont ignorés.
        # Cette règle est cohérente avec PrepareEntreesJpegs (séries plates uniquement).

        jpg_dir = Path(l_sz_jpg_scans)
        jpg_files = sorted([
            f.name for f in jpg_dir.iterdir()
            if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg"}
        ])

        print(f"Found {len(jpg_files)} JPEG(s) to process in parallel...")

        tasks = []
        for file_name in jpg_files:
            src = os.path.join(l_sz_jpg_scans, file_name)
            big   = os.path.join(l_sz_big, file_name)
            view  = os.path.join(l_sz_view, file_name)
            contact = os.path.join(l_sz_contact_sheet, file_name)
            tasks.append((src, big, view, contact, 1935))

        # Use ProcessPoolExecutor for CPU-bound image resizing (best with pillow-simd)
        max_workers = max(1, (os.cpu_count() or 4) - 1)   # leave one core free
        print(f"Using up to {max_workers} parallel workers")

        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_one_image, *task) for task in tasks]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()   # will raise if the task failed
                except Exception as e:
                    print(f"Task failed: {e}")

        print("ResizeJpegs finished.")
        return
