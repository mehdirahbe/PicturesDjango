import struct
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from PIL import Image
from PIL.ExifTags import TAGS
import requests
from PicturesApp.PhotoModel import PhotoModel
from django.db.models import Q
import time
from django.conf import settings


def get_exif_data(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = {
                TAGS[key]: value
                for key, value in img._getexif().items()
                if key in TAGS
            }
        return exif_data
    except Exception:
        return None


def extract_date(exif_data):
    if exif_data is not None and 'DateTimeOriginal' in exif_data:
        date_str = exif_data['DateTimeOriginal']
        date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        return date
    return None


def get_gps_coordinates(exif_data):
    if 'GPSInfo' in exif_data:
        gps_info = exif_data['GPSInfo']
        lat = gps_info.get(2, ())
        lon = gps_info.get(4, ())
        if lat and lon:
            lat_ref = gps_info.get(1, 'N')
            lon_ref = gps_info.get(3, 'E')
            lat = convert_to_degrees(lat)
            lon = convert_to_degrees(lon)
            if lat_ref == 'S':
                lat = -lat
            if lon_ref == 'W':
                lon = -lon
            return lat, lon
    return None, None


def convert_to_degrees(value):
    d = value[0]
    m = value[1]
    s = value[2]
    return d + (m / 60.0) + (s / 3600.0)


def _fetch_nominatim_address(lat, lon):
    """Appel Nominatim et retourne le dict 'address' brut (ou None)."""
    url = f'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}&zoom=12&language=fr'
    headers = {'User-Agent': 'PicturesDjango/1.1', 'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'}
    try:
        response = requests.get(url, headers=headers, timeout=10).json()
        return response.get('address') if response else None
    except Exception:
        return None


def build_short_location(address):
    """
    Construit un texte de localisation court, lisible et utile pour un humain.
    Exemples : "Fredericia, Danemark", "Annecy, Haute-Savoie, France"
    Style volontairement concis (on a le lien Google Maps de toute façon).
    """
    if not address:
        return None

    # Ordre de priorité pour le nom de lieu principal (le plus parlant)
    place_keys = ['village', 'town', 'city', 'hamlet', 'suburb']
    place = None
    for key in place_keys:
        if address.get(key):
            place = address[key]
            break

    # Deuxième niveau administratif utile (sans redondance)
    second_keys = ['county', 'state_district', 'state']
    second = None
    for key in second_keys:
        val = address.get(key)
        if val and val != place:
            second = val
            break

    country = address.get('country')

    parts = [p for p in [place, second, country] if p]
    if not parts:
        return None

    # Petit nettoyage anti-redondance
    if place == country:
        parts = [place, country]
    elif second == country:
        parts = [place, country] if place else [country]

    return ", ".join(parts)


# ============================================================
# === Extraction des données techniques EXIF =================
# ============================================================

def _get_exif_tag(exif_data, tag_name):
    """Récupère une valeur EXIF de façon sûre."""
    if not exif_data:
        return None
    return exif_data.get(tag_name)


def _rational_to_float(value):
    """Convertit de façon robuste n'importe quel type EXIF rationnel en float."""
    if value is None:
        return None

    # Déjà un nombre
    if isinstance(value, (int, float)):
        return float(value)

    # Tuple ou liste (num, den) classique
    if isinstance(value, (list, tuple)) and len(value) == 2:
        num, den = value
        if den != 0:
            return num / den

    # Fraction (utilisé par certaines versions de Pillow)
    try:
        from fractions import Fraction
        if isinstance(value, Fraction):
            return float(value)
    except ImportError:
        pass

    # Dernier recours : essayer de caster
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def format_focal_length(value):
    """Retourne une focale lisible, ex: '85 mm' ou '24-70 mm'."""
    if value is None:
        return None

    # Cas où c'est déjà une string
    if isinstance(value, str):
        return value if 'mm' in value.lower() else value + ' mm'

    # Cas rationnel simple (50 mm)
    fl = _rational_to_float(value)
    if fl is not None:
        return f"{fl:.0f} mm" if fl == int(fl) else f"{fl:.1f} mm"

    return None


def format_aperture(value):
    """Retourne l'ouverture, ex: 'f/2.8'."""
    if value is None:
        return None
    fnum = _rational_to_float(value)
    if fnum is None or fnum <= 0:
        return None
    try:
        if abs(fnum - round(fnum)) < 1e-6:   # très proche d'un entier
            return f"f/{int(round(fnum))}"
        else:
            return f"f/{fnum:.1f}".rstrip('0').rstrip('.')
    except Exception:
        return None


def _apex_to_fnumber(apex_value):
    """Convertit une valeur ApertureValue (APEX) en f-number."""
    try:
        apex = _rational_to_float(apex_value)
        if apex is not None:
            return 2 ** (apex / 2.0)
    except Exception:
        pass
    return None


def format_shutter_speed(value):
    """Retourne le temps de pose formaté joliment."""
    if value is None:
        return None

    if isinstance(value, str):
        return value

    fl = _rational_to_float(value)
    if fl is None or fl <= 0:
        return None

    try:
        if fl >= 1:
            return f"{fl:.1f} s".rstrip('0').rstrip('.')
        else:
            reciprocal = 1.0 / fl
            # On arrondit pour éviter les artefacts de float (ex: 260.99999)
            return f"1/{int(round(reciprocal))} s"
    except Exception:
        return None


def _apex_shutter_to_seconds(apex_value):
    """Convertit une valeur ShutterSpeedValue (APEX) en secondes."""
    try:
        apex = _rational_to_float(apex_value)
        if apex is not None:
            return 2 ** (-apex)
    except Exception:
        pass
    return None


def _clean_brand_name(brand):
    """
    Nettoie le nom de la marque selon la règle :
    - S'il contient au moins une voyelle → première lettre en majuscule, le reste en minuscules.
    - Sinon (acronyme style LG, DJI, HTC) → tout en majuscules.
    """
    if not brand:
        return ""
    brand = brand.strip()
    vowels = set("aeiouyAEIOUY")
    has_vowel = any(c in vowels for c in brand)

    if has_vowel:
        return brand[0].upper() + brand[1:].lower()
    else:
        return brand.upper()


def get_camera_name(exif_data):
    """Construit un nom d'appareil lisible et bien formaté."""
    make = _get_exif_tag(exif_data, 'Make')
    model = _get_exif_tag(exif_data, 'Model')

    make = _clean_brand_name(make) if make else ""
    model = model.strip() if model else ""

    if make and model:
        # Évite les doublons du style "Samsung Samsung Galaxy A14"
        if model.lower().startswith(make.lower()):
            return model
        return f"{make} {model}"
    if model:
        return model
    if make:
        return make
    return None


def extract_technical_exif(exif_data):
    """
    Extrait et formate les données techniques principales.
    Retourne un dict avec les clés correspondant aux champs du modèle.
    """
    if not exif_data:
        return {}

    result = {}

    # Appareil
    camera = get_camera_name(exif_data)
    if camera:
        result['appareil'] = camera

    # Focale
    focal = format_focal_length(_get_exif_tag(exif_data, 'FocalLength'))
    if focal:
        result['focale'] = focal

    # Diaphragme (FNumber est prioritaire, ApertureValue en fallback pour beaucoup de smartphones)
    aperture = format_aperture(_get_exif_tag(exif_data, 'FNumber'))
    if not aperture:
        apex_aperture = _get_exif_tag(exif_data, 'ApertureValue')
        if apex_aperture:
            fnum = _apex_to_fnumber(apex_aperture)
            aperture = format_aperture(fnum)
    if aperture:
        result['diaphragme'] = aperture

    # Temps de pose (ExposureTime prioritaire, ShutterSpeedValue en fallback)
    shutter = format_shutter_speed(_get_exif_tag(exif_data, 'ExposureTime'))
    if not shutter:
        apex_shutter = _get_exif_tag(exif_data, 'ShutterSpeedValue')
        if apex_shutter:
            seconds = _apex_shutter_to_seconds(apex_shutter)
            shutter = format_shutter_speed(seconds)
    if shutter:
        result['temps_pose'] = shutter

    # ISO - peut arriver sous forme de tuple/list sur certains appareils
    iso = _get_exif_tag(exif_data, 'ISOSpeedRatings')
    if iso:
        try:
            if isinstance(iso, (list, tuple)):
                iso = iso[0] if iso else None
            if iso:
                result['iso'] = int(iso)
        except (ValueError, TypeError, IndexError):
            pass

    return result


class Command(BaseCommand):
    help = (
        'Extract EXIF information from images of a given series:\n'
        '  - Date de prise de vue\n'
        '  - Coordonnées GPS + localisation (sujet_dias, uniquement si vide)\n'
        '  - Données techniques (appareil, focale, diaphragme, temps de pose, ISO)\n\n'
        'Syntax: python manage.py ExtractEXIFInfos --SubjectMD5 <md5>\n\n'
        'Note: pour remplir les nouveaux champs techniques sur toute la base, '
        'il faut relancer la commande sur chaque série (SubjectMD5).')

    def add_arguments(self, parser):
        parser.add_argument(
            '--SubjectMD5',
            type=str,
            default=None,
            help='Optional. If not provided, the command will process ALL series (full backfill).'
        )

    def handle(self, *args, **options):
        desiredsubjectMD5=options["SubjectMD5"]
        dias_dir = settings.IMAGES_PATH

        # Construction du queryset
        if desiredsubjectMD5:
            print(f"Mode: Single series (MD5={desiredsubjectMD5})")
            allphotos = PhotoModel.objects.filter(
                checksum=desiredsubjectMD5
            ).filter(
                Q(premier_niveau__isnull=False) & ~Q(premier_niveau='')
            ).filter(agrandi=True)
        else:
            print("Mode: FULL BACKFILL (all series)")
            print("→ Technical EXIF will be filled where missing.")
            print("→ Reverse geocoding is limited to 99 calls per run (existing protection).")
            allphotos = PhotoModel.objects.filter(
                Q(premier_niveau__isnull=False) & ~Q(premier_niveau='')
            ).filter(agrandi=True).filter(
                Q(nom_fichier_jpeg__isnull=False) & ~Q(nom_fichier_jpeg='')
            )

        total_photos = allphotos.count()
        print(f"Found {total_photos} photos to process.\n")

        #we have to limit number of calls
        countCallsReverseGPS = 0
        countRecUpdated = 0
        #cache to avoid calls on same address
        dicoGPSToAddress = {}

        for idx, photo in enumerate(allphotos, start=1):
            try:
                # Image path
                photo_path = os.path.join(dias_dir, "scans", photo.premier_niveau, photo.second_niveau)
                if photo.troisieme_niveau:
                    photo_path = os.path.join(str(photo_path), photo.troisieme_niveau)
                photo_path = os.path.join(str(photo_path), photo.nom_fichier_jpeg)

                recUpdated = False
                exif = get_exif_data(photo_path)
                if exif is not None:
                    date = extract_date(exif)
                    if date is not None:
                        date_formatee = date.strftime('%d/%m/%Y')
                        if photo.date != date_formatee:
                            photo.date = date_formatee
                            recUpdated = True

                    # --- Données techniques (appareil, focale, diaphragme, etc.) ---
                    # On vérifie champ par champ. On n'appelle l'extraction que si au moins
                    # un champ technique est encore vide.
                    tech_fields = ['appareil', 'focale', 'diaphragme', 'temps_pose', 'iso']
                    needs_tech = any(
                        not getattr(photo, f) or (isinstance(getattr(photo, f), str) and not str(getattr(photo, f)).strip())
                        for f in tech_fields
                    )

                    if needs_tech:
                        tech = extract_technical_exif(exif)
                        if tech:
                            for field, value in tech.items():
                                current = getattr(photo, field, None)
                                if not current or (isinstance(current, str) and not str(current).strip()):
                                    setattr(photo, field, value)
                                    recUpdated = True

                    # --- Localisation + GPS ---
                    if photo.longitude is None or not (photo.sujet_dias or '').strip():
                        lat, lon = get_gps_coordinates(exif)
                        if lat is not None and lon is not None:
                            if photo.longitude is None:
                                photo.longitude = lon
                                photo.latitude = lat
                                recUpdated = True
                            if not (photo.sujet_dias or '').strip():
                                    #create a key from lat and lon keeping 2 digits, meaning about 1 km précision
                                    gpsKey = (1000 * int(lat * 100.) + int(lon * 100.))
                                    if gpsKey in dicoGPSToAddress:
                                        print("from GPS cache: "+str(gpsKey)+" "+str(dicoGPSToAddress[gpsKey]))
                                        if dicoGPSToAddress[gpsKey]:
                                            photo.sujet_dias = dicoGPSToAddress[gpsKey]
                                            recUpdated = True
                                    else:
                                        countCallsReverseGPS = countCallsReverseGPS + 1
                                        if countCallsReverseGPS < 100:
                                            '''From grok: La politique d'utilisation 
                                            de Nominatim recommande explicitement de ne pas dépasser 1 requête par 
                                            seconde. Cela signifie que vous devez intégrer un délai d'au moins 1 seconde 
                                            entre chaque appel à l'API.'''
                                            time.sleep(1.1)
                                            print("ask reverse for "+ str(lat)+" "+ str(lon))
                                            raw_address = _fetch_nominatim_address(lat, lon)
                                            nice_location = build_short_location(raw_address)
                                            print("address is "+ str(nice_location))
                                            dicoGPSToAddress[gpsKey] = nice_location
                                            if nice_location:
                                                photo.sujet_dias = nice_location
                                                recUpdated = True
                                        else:
                                            print("reverse GPS not done, call count is " + str(countCallsReverseGPS))

                # Sauvegarder le modèle
                if recUpdated:
                    countRecUpdated = countRecUpdated + 1
                    photo.save()

                # === Progress reporting (toutes les 200 photos) ===
                if idx % 200 == 0 or idx == total_photos:
                    print(f"[{idx}/{total_photos}]  Mis à jour jusqu'ici: {countRecUpdated}  |  Appels GPS utilisés: {countCallsReverseGPS}/99")

            except Exception as e:
                print(f"Erreur lors du traitement de l'image  {e}")

        print("\n=== Terminé ===")
        print(f"number of updated records: {countRecUpdated}")
        print(f"Total appels Nominatim effectués: {countCallsReverseGPS}")
        return


