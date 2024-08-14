import os
from PIL import Image, ExifTags

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

def resize_image(in_file, out_files, desired_max_sizes):
    try:
        with Image.open(in_file) as src_image:
            src_image = apply_orientation(src_image)
            max_dimension = max(src_image.width, src_image.height)
            for out_file, desired_max_size in zip(out_files, desired_max_sizes):
                scale_factor = 1.0
                if max_dimension > desired_max_size:
                    scale_factor = desired_max_size / max_dimension
                new_width = int(src_image.width * scale_factor)
                new_height = int(src_image.height * scale_factor)
                new_image = src_image.resize((new_width, new_height), Image.LANCZOS)
                new_image.save(out_file, "JPEG", quality=95)
    except Exception as e:
        print(f"Got exception {e}")

def handle_image(psz_tif, psz_jpg_scan, psz_big, psz_contact_sheet, psz_view, p_b_from300d):
    if psz_tif:
        pass  # High-quality conversion from TIF to JPG if needed

    l_n_desired_size = 1935
    if psz_big:
        print(f"Convert \"{psz_jpg_scan}\" to \"{psz_big}\"")
        l_n_desired_sizes = [l_n_desired_size, l_n_desired_size // 2, l_n_desired_size // 10]
        reduced_files = [psz_big, psz_view, psz_contact_sheet]
        resize_image(psz_jpg_scan, reduced_files, l_n_desired_sizes)

def handle_all_tifs(psz_scanned_tifs_dir, psz_jpg_scans):
    pass  # Implementation if needed for TIF files

def handle_jpeg_scans(psz_big, psz_contact_sheet, psz_view, psz_jpg_scans, p_b_from300d):
    file_entries = os.listdir(psz_jpg_scans)
    for file_name in file_entries:
        if file_name.lower().endswith(".jpg"):
            l_sz_jpg_scan = os.path.join(psz_jpg_scans, file_name)
            l_sz_big = os.path.join(psz_big, file_name)
            l_sz_view = os.path.join(psz_view, file_name)
            l_sz_contact_sheet = os.path.join(psz_contact_sheet, file_name)
            handle_image(None, l_sz_jpg_scan, l_sz_big, l_sz_contact_sheet, l_sz_view, p_b_from300d)

def do_the_job(psz_scanned_tifs_dir, psz_big, psz_contact_sheet, psz_view, psz_jpg_scans, p_b_from300d):
    if not p_b_from300d:
        handle_all_tifs(psz_scanned_tifs_dir, psz_jpg_scans)
    handle_jpeg_scans(psz_big, psz_contact_sheet, psz_view, psz_jpg_scans, p_b_from300d)

if __name__ == "__main__":
    import sys
    print(sys.argv)

    l_b_from300d = True
    if len(sys.argv) < 5:
        print("Usage: converter [series dest directory, ie voyages/amsterdam_TreldeNaes_Hoganas_2024] [n/f if not from 300D, default=300D, ie y], [optional: scanned tifs rep, ie dummy] [optional: dias root dir, ie /home/mehdi/Images]")
        sys.exit(-1)

    if len(sys.argv) > 1:
        l_c_param = sys.argv[2].lower()[0]
        if l_c_param in ('n', 'f'):
            l_b_from300d = False

    sz_scanned_tifs_dir = sys.argv[3]
    sz_dias_root_dir = sys.argv[4]
    sz_series_dest_dir = sys.argv[1]

    l_sz_root_serie = os.path.join(sz_dias_root_dir, sz_series_dest_dir)
    l_sz_big = os.path.join(l_sz_root_serie, "big")
    l_sz_contact_sheet = os.path.join(l_sz_root_serie, "contactsheet")
    l_sz_view = os.path.join(l_sz_root_serie, "view")
    l_sz_jpg_scans = os.path.join(sz_dias_root_dir, "scans", sz_series_dest_dir)

    os.makedirs(l_sz_root_serie, exist_ok=True)
    os.makedirs(l_sz_big, exist_ok=True)
    os.makedirs(l_sz_contact_sheet, exist_ok=True)
    os.makedirs(l_sz_view, exist_ok=True)
    os.makedirs(l_sz_jpg_scans, exist_ok=True)

    do_the_job(sz_scanned_tifs_dir, l_sz_big, l_sz_contact_sheet, l_sz_view, l_sz_jpg_scans, l_b_from300d)

