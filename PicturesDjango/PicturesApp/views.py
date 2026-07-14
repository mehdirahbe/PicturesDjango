import hashlib
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, FileResponse
from django.core.cache import cache
from django.contrib import messages
from django.utils.translation import gettext as _
import os
import re
from django.db.models import Q, Count, Case, When, Value, IntegerField
from django.conf import settings
from unidecode import unidecode
from rapidfuzz import fuzz
from .forms import SearchForm, InsertNewPicturesForm, PhotoSubjectForm
from .PhotoModel import PhotoModel
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

SEARCH_CACHE_VERSION_KEY = 'search:cache_version'


def _search_cache_version():
    return cache.get(SEARCH_CACHE_VERSION_KEY, 0)


def _search_cache_key(normalized, apply_fuzzy, fuzzy_threshold):
    return f"search:{_search_cache_version()}:{normalized}:{apply_fuzzy}:{fuzzy_threshold}"


def invalidate_search_cache():
    """Bump search cache version so new imports appear in search results immediately."""
    try:
        cache.incr(SEARCH_CACHE_VERSION_KEY)
    except ValueError:
        cache.set(SEARCH_CACHE_VERSION_KEY, 1, timeout=None)


def _get_worst_exposure_photos(photos, limit=5):
    """
    Parmi une liste de photos déjà analysées, retourne les 'limit' pires
    sur le critère d'exposition (trop sombres ou trop claires).
    Photos sans métriques → ignorées.
    """
    analyzed = [p for p in photos if p.luminance_mean is not None]
    if not analyzed:
        return []

    def exposure_problem_score(p):
        dev = abs(p.luminance_mean - 128.0) / 128.0
        max_clip = max(p.shadow_clip_pct or 0.0, p.highlight_clip_pct or 0.0)
        # Pondération : 65% écart à la moyenne, 35% sur les zones clipées
        return (dev * 0.65) + (max_clip / 100.0 * 0.35)

    return sorted(analyzed, key=exposure_problem_score, reverse=True)[:limit]


def get_search_queryset(search_term, apply_fuzzy=True, fuzzy_threshold=75):
    """
    Recherche full-text multi-mots avec fuzzy (rapidfuzz) - Mode Option A strict (règle dure).

    Phase 1 - Mot exact:
        Pour chaque mot de la requête, récupération large par icontains exact (pas de fuzzy, pas de prefix).
        Union via OR (Q objects) : un record avec typo "furte" est ramené grâce aux autres mots exacts
        présents dans ses données (ex: "david" + "2013").

    Phase 2 - Règle dure pour filtrer:
        Pour chaque photo candidate, pour chaque mot de recherche :
          - Si mot = année (isdigit) → match EXACT obligatoire dans les tokens (pas de fuzzy).
          - Sinon → meilleur score WRatio sur les tokens individuels des champs.
        Si UN SEUL mot a un score < fuzzy_threshold → exclusion totale (continue).
        Photos qui passent la porte dure mais avec un score hybride très faible sont aussi éliminées
        (floor sur final_score) pour éviter le bruit "année + fuzzy faible" en fin de liste.

    Seuil 75 par défaut (relevé pour supprimer le bruit tout en préservant les typos utiles
    comme "davud"→"david", "furte"↔"fuerte" etc.).
    """
    if not search_term or not search_term.strip():
        return PhotoModel.objects.none()

    normalized = unidecode(search_term).lower().strip()
    words = [w for w in normalized.split() if len(w) >= 2]

    if not words:
        # On met aussi en cache les recherches vides pour éviter des recalculs inutiles
        cache_key = _search_cache_key(normalized, apply_fuzzy, fuzzy_threshold)
        cache.set(cache_key, [], timeout=900)
        return PhotoModel.objects.none()

    # ========== CACHE ==========
    # On met en cache la liste des pkeys (et non les objets complets) pour éviter
    # de recalculer le scoring fuzzy à chaque affichage de la planche ou de la galerie.
    cache_key = _search_cache_key(normalized, apply_fuzzy, fuzzy_threshold)
    cached_pkeys = cache.get(cache_key)

    if cached_pkeys is not None:
        # Reconstruction de la liste ordonnée à partir des pkeys en cache
        photos = list(PhotoModel.objects.filter(pkey__in=cached_pkeys))
        photo_dict = {p.pkey: p for p in photos}
        ordered_photos = [photo_dict[pk] for pk in cached_pkeys if pk in photo_dict]
        return ordered_photos

    # ========== PHASE 1 : Récupération LARGE par mot EXACT (union OR) ==========
    # Les records sont trouvés via les mots exacts (david, 2013...). Pas de fuzzy ici.
    base_filter = Q(agrandi=True) & Q(premier_niveau__isnull=False)

    candidates_qs = PhotoModel.objects.none()

    for word in words:
        word_q = (
            Q(sujet_dias__icontains=word) |
            Q(commentaire__icontains=word) |
            Q(lieu__icontains=word) |
            Q(date__icontains=word) |
            Q(sujet__icontains=word)
        )
        candidates_qs |= PhotoModel.objects.filter(base_filter & word_q)

    # On ramène un pool large (le filtrage dur se fait en phase 2)
    candidates = list(
        candidates_qs.distinct().order_by('pkey')[:3000]
    )

    if not apply_fuzzy:
        return candidates[:1000]

    # ========== PHASE 2 : RÈGLE DURE + scoring hybride ==========
    scored_photos = []

    for photo in candidates:
        # Tokenisation de tous les champs texte (mots >= 2 chars)
        raw_tokens = set()
        for field in (photo.sujet_dias, photo.commentaire, photo.lieu, photo.date, photo.sujet):
            if field:
                for tok in re.split(r'[^a-z0-9]+', field.lower()):
                    if len(tok) >= 2:
                        raw_tokens.add(tok)

        # Note: on garde les tokens tels quels (david's reste "david's") pour ne pas être trop permissif
        photo_tokens = raw_tokens

        word_scores = []
        exact_in_sujet_dias = 0

        for word in words:
            best_score = 0

            # 1) Match exact sur token ?
            if word in photo_tokens:
                best_score = 100
                # Boost très fort si l'exact match est dans sujet_dias (règle métier)
                if photo.sujet_dias:
                    dias_tokens = re.split(r'[^a-z0-9]+', photo.sujet_dias.lower())
                    if word in dias_tokens:
                        exact_in_sujet_dias += 1
            elif word.isdigit():
                # Année : EXACT obligatoire, pas de fuzzy (règle dure)
                best_score = 0
            else:
                # Fuzzy mot-à-mot (sur tokens individuels, plus précis que sur phrase entière)
                # On ignore volontairement les tout petits tokens ("la", "de", "au", "me", "en"...)
                # car ils font gonfler artificiellement le WRatio sur des mots longs ("montblanc")
                # et font fuiter du bruit en fin de résultats.
                if photo_tokens:
                    min_tok_len = max(3, len(word) - 2)
                    for tok in photo_tokens:
                        if len(tok) < min_tok_len:
                            continue
                        score = fuzz.WRatio(word, tok)
                        if score > best_score:
                            best_score = score

            word_scores.append(best_score)

        min_word_score = min(word_scores) if word_scores else 0

        # === RÈGLE DURE (Option A stricte) : un seul mot en dessous du seuil → EXCLUSION TOTALE (pas dans les résultats) ===
        if min_word_score < fuzzy_threshold:
            # On ne garde pas la photo du tout (c''est la "règle dure pour filtrer")
            continue

        # Score hybride : priorité aux matches exacts + qualité fuzzy + boost sujet_dias
        num_exact = sum(1 for s in word_scores if s >= 99)
        avg_fuzzy = sum(word_scores) / len(word_scores)

        # Base forte pour les matches exacts (chaque mot exact = gros poids)
        base = num_exact * 12
        # Bonus supplémentaire très important pour les matches dans sujet_dias (exigence utilisateur)
        base += exact_in_sujet_dias * 18

        # Partie fuzzy (qualité de la tolérance typo) + récompense forte du pire mot (plus strict sur la "règle dure")
        final_score = base + (avg_fuzzy * 0.25) + (min_word_score * 0.35)

        # Floor de sécurité : même si on a passé la porte dure, si le score global reste très faible
        # (typiquement "une année + un mot avec fuzzy juste au-dessus du seuil et rien d'autre"),
        # on élimine pour ne pas polluer la fin des résultats.
        if final_score < 12:
            continue

        scored_photos.append((final_score, photo))

    # Tri par score final (les bons matches avec tous mots forts remontent en premier)
    scored_photos.sort(key=lambda x: x[0], reverse=True)

    # Limite finale 1000 (cohérent avec les autres galeries)
    final_results = [p for _, p in scored_photos[:1000]]

    # Mise en cache des pkeys (pour éviter de recalculer le fuzzy sur les affichages suivants)
    pkeys = [p.pkey for p in final_results]
    cache.set(cache_key, pkeys, timeout=900)  # 15 minutes

    return final_results


# Function to generate a Google Maps link if coordinates are available
def GetLinkToGoogleMaps(photo):
    """
    Generate a Google Maps link if the photo has latitude and longitude.

    Args:
    - photo (PhotoModel): The photo object to check for coordinates.

    Returns:
    - str or None: URL to Google Maps or None if no coordinates are available.
    """
    if photo is None:
        return None
    if photo.latitude is not None and photo.longitude is not None:
        link = f"https://www.google.com/maps/search/?api=1&query={photo.latitude},{photo.longitude}"
        return link
    return None


def search_form(request):
    """
    Handle the search form submission.

    If POST, validate the form and redirect to search results.
    If GET, display the search form.

    Args:
    - request (HttpRequest): The HTTP request object.

    Returns:
    - HttpResponse: Redirects to search results or renders the form.
    """
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_term = form.cleaned_data['search_term']
            return redirect('ContactsSheetBySearch', search_term=search_term)
    else:
        form = SearchForm()
    return render(request, 'search_form.html', {'form': form})


def home(request):
    """
    Display the home page with first level categories.

    Uses pagination to manage large datasets.

    Also handles the "Copy to smartphone" action via POST.
    """
    if request.method == 'POST' and request.POST.get('action') == 'copy_to_smartphone':
        try:
            call_command('copy_images_for_smartphone')
            messages.success(request, _("Smartphone folder prepared successfully."))
        except Exception as e:
            messages.error(request, _("Error while preparing smartphone folder: {}").format(e))

        return redirect(request.path_info)

    photo_niveaux = (
        PhotoModel.objects
        .filter(Q(premier_niveau__isnull=False) & ~Q(premier_niveau=''))
        .values('premier_niveau')
        .annotate(count=Count('pkey'))
        .order_by('premier_niveau')
    )
    paginator = Paginator(photo_niveaux, 100)  # Show 100 items per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'home.html', context)


def DisplaySecondLevel(request, firstLevel):
    """
    Display photos categorized by second level, with optional third level.

    Args:
    - request (HttpRequest): The HTTP request object.
    - firstLevel (str): The first level category to filter by.

    Returns:
    - HttpResponse: Renders the second level page with paginated data.
    """
    allphotos = PhotoModel.objects.filter(premier_niveau=firstLevel).filter(
        Q(second_niveau__isnull=False) & ~Q(second_niveau=''))

    photo_niveaux = allphotos.values_list('second_niveau', 'troisieme_niveau', 'checksum', 'sujet').distinct().annotate(
        count=Count('pkey')).order_by('sujet')

    paginator = Paginator(photo_niveaux, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'secondlevel.html', context)


def photo_Jpeg(request, photo_id, size):
    """
    Serve a JPEG image based on its ID and desired size.

    - Uses FileResponse for streaming (better memory usage than loading the whole file).
    - Explicitly handles photos without a scanned JPEG (historical slides).

    Args:
    - request (HttpRequest): The HTTP request object.
    - photo_id (int): The primary key of the photo.
    - size (str): The size of the image to return ('big', 'view' or 'contactsheet').

    Returns:
    - FileResponse: The JPEG stream, or raises Http404 with a clear message.
    """
    ALLOWED_SIZES = {'big', 'view', 'contactsheet'}
    if size not in ALLOWED_SIZES:
        raise Http404("Invalid size")

    try:
        photo = PhotoModel.objects.get(pkey=photo_id)

        if not photo.nom_fichier_jpeg:
            # This entry corresponds to a physical slide that was never scanned
            raise Http404("No scanned image available for this slide.")

        base_path = Path(settings.IMAGES_PATH) / photo.premier_niveau / photo.second_niveau
        if photo.troisieme_niveau:
            base_path = base_path / photo.troisieme_niveau

        jpeg_path = base_path / size / photo.nom_fichier_jpeg

        return FileResponse(open(jpeg_path, 'rb'), content_type='image/jpeg')

    except PhotoModel.DoesNotExist:
        raise Http404("Photo not found")
    except FileNotFoundError:
        raise Http404("Image file not found on disk")
    except Exception:
        logger.exception("Unexpected error while serving photo pkey=%s size=%s", photo_id, size)
        raise Http404("Image not found")


def photoDetail(request, photo_id):
    """
    Display details of a photo, including location and comments.

    Args:
    - request (HttpRequest): The HTTP request object.
    - photo_id (int): The primary key of the photo.

    Returns:
    - HttpResponse: Renders the photo detail page or form submission result.
    """
    try:
        photo = PhotoModel.objects.get(pkey=photo_id)
    except PhotoModel.DoesNotExist:
        raise Http404("Photo not found")

    if request.method == 'POST':
        form = PhotoSubjectForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path_info)
    else:
        form = PhotoSubjectForm(instance=photo)

    return render(request, 'photo_detail.html', {
        'photoRec': photo,
        'linktogooglemaps': GetLinkToGoogleMaps(photo),
        'subject_form': form
    })


def contactsSheet(request, desiredsubjectMD5):
    """
    Display a contact sheet of photos with a specific MD5 checksum.

    Args:
    - request (HttpRequest): The HTTP request object.
    - desiredsubjectMD5 (str): The MD5 checksum of the subject.

    Returns:
    - HttpResponse: Renders the contact sheet (possibly empty).
    """
    base_qs = PhotoModel.objects.filter(checksum=desiredsubjectMD5).filter(agrandi=True)
    total_count = base_qs.count()
    if total_count > 1000:
        logger.warning(
            "Troncature de la planche contact pour le sujet MD5=%s : %d photos trouvées (>1000), limité à 1000.",
            desiredsubjectMD5, total_count
        )
    allphotos = base_qs.order_by('pkey')[:1000]

    if request.method == 'POST' and request.POST.get('action') == 'resize':
        photo = allphotos.first()
        if photo:
            parts = [photo.premier_niveau, photo.second_niveau]
            if photo.troisieme_niveau:
                parts.append(photo.troisieme_niveau)
            seriesdestdirectory = '/'.join(parts)

            try:
                call_command('ResizeJpegs', seriesdestdirectory=seriesdestdirectory)
                messages.success(request, _("Intelligent resizing re-triggered successfully."))
            except Exception as e:
                logger.exception("Resize failed for MD5=%s", desiredsubjectMD5)
                messages.error(request, _("Error during resizing: {}").format(e))

        return redirect(request.path_info)

    if request.method == 'POST' and request.POST.get('action') == 'analyze_quality':
        try:
            call_command('AnalyzePhotoQuality', SubjectMD5=desiredsubjectMD5)
            messages.success(request, _("Exposure quality analysis completed for this series."))
        except Exception as e:
            logger.exception("Quality analysis failed for MD5=%s", desiredsubjectMD5)
            messages.error(request, _("Error during analysis: {}").format(e))
        return redirect(f"{request.path_info}?show_quality=1")

    show_quality = request.GET.get('show_quality') == '1'
    worst_photos = _get_worst_exposure_photos(allphotos) if show_quality else []

    return render(
        request,
        'contactsSheet.html',
        {
            'photoRecs': allphotos,
            'desiredsubjectMD5': desiredsubjectMD5,
            'worst_photos': worst_photos,
        }
    )


def Gallery(request, desiredsubjectMD5):
    """
    Display photos in a gallery format for a specific subject.

    Args:
    - request (HttpRequest): The HTTP request object.
    - desiredsubjectMD5 (str): The MD5 checksum of the subject.

    Returns:
    - HttpResponse: Renders the gallery (possibly empty).
    """
    base_qs = PhotoModel.objects.filter(checksum=desiredsubjectMD5).filter(agrandi=True)
    total_count = base_qs.count()
    if total_count > 1000:
        logger.warning(
            "Troncature de la galerie pour le sujet MD5=%s : %d photos trouvées (>1000), limité à 1000.",
            desiredsubjectMD5, total_count
        )
    allphotos = base_qs.order_by('pkey')[:1000]
    paginator = Paginator(allphotos, 1)
    page_number = request.GET.get('page')
    photos_page = paginator.get_page(page_number)

    try:
        photo = photos_page[0]
    except (IndexError, TypeError):
        photo = None

    return render(request, 'gallery.html', {
        'photo': photo,
        'photos': photos_page,
        'desiredsubjectMD5': desiredsubjectMD5,
        'linktogooglemaps': GetLinkToGoogleMaps(photo)
    })


def contactsSheetBySearch(request, search_term):
    """
    Display a contact sheet of photos matching the search term.

    Args:
    - request (HttpRequest): The HTTP request object.
    - search_term (str): The term to search for.

    Returns:
    - HttpResponse: Renders the search result contact sheet (possibly empty).
    """
    allphotos = get_search_queryset(search_term)
    return render(request, 'contactsSheetBySearch.html', {'photoRecs': allphotos, 'search_term': search_term})


def GalleryBySearch(request, search_term):
    """
    Display photos in a gallery format matching the search term.

    Args:
    - request (HttpRequest): The HTTP request object.
    - search_term (str): The term to search for.

    Returns:
    - HttpResponse: Renders the search result gallery (possibly empty).
    """
    allphotos = get_search_queryset(search_term)
    paginator = Paginator(allphotos, 1)
    page_number = request.GET.get('page')
    photos_page = paginator.get_page(page_number)

    photo = photos_page[0] if photos_page else None

    return render(request, 'galleryBySearch.html', {
        'photo': photo,
        'photos': photos_page,
        'search_term': search_term,
        'linktogooglemaps': GetLinkToGoogleMaps(photo)
    })


def InsertNewPictures(request):
    """
    Handle the insertion of new pictures into the system.

    This view processes new JPEG files, adds entries to the database,
    resizes images, and extracts EXIF information.

    Args:
    - request (HttpRequest): The HTTP request object.

    Returns:
    - HttpResponse: Redirects to the contact sheet of newly added images or renders the form.
    """
    initial = {}
    if request.method == 'GET':
        jpegsdirectory = request.GET.get('jpegsdirectory')
        if jpegsdirectory:
            initial['jpegsdirectory'] = jpegsdirectory
    if request.method == 'POST':
        form = InsertNewPicturesForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data

            jpegsdirectory = cleaned['jpegsdirectory']
            subject = cleaned['subject']
            date = cleaned['date']
            comment = cleaned['comment']

            # The directory has already been validated by the form's clean_jpegsdirectory()
            # (must be under IMAGES_PATH/scans and must exist)
            base_path = os.path.join(settings.IMAGES_PATH, "scans")
            seriesdestdirectory = jpegsdirectory[len(base_path):].strip(os.sep)

            # Use the new high-level ImportSeries command.
            # It orchestrates:
            #   1. Smart resizing (file-by-file, only what is needed)
            #   2. If resizing succeeds → atomic (Prepare + ExtractEXIF) inside a transaction
            try:
                call_command(
                    'ImportSeries',
                    jpegsdirectory=jpegsdirectory,
                    subject=subject,
                    date=date,
                    comment=comment,
                )
            except CommandError as e:
                logger.exception("ImportSeries failed for %s", jpegsdirectory)
                messages.error(request, _("Import failed: {}").format(e))
                return render(request, 'InsertNewPictures.html', {'form': form})

            invalidate_search_cache()

            # Generate the MD5 (still needed for the redirect to the contact sheet)
            desiredsubjectMD5 = hashlib.md5(subject.encode(), usedforsecurity=False).hexdigest()

            # Redirect to the contact sheet of the newly imported series
            return redirect('ContactsSheet', desiredsubjectMD5=desiredsubjectMD5)
        else:
            return render(request, 'InsertNewPictures.html', {'form': form})
    else:
        form = InsertNewPicturesForm(initial=initial)

    return render(request, 'InsertNewPictures.html', {'form': form})

def list_missing_scans(request):
    scans_root = Path(settings.IMAGES_PATH) / "scans"
    images_root = Path(settings.IMAGES_PATH)

    def get_subdirs(root):
        subdirs = {}
        for dirpath, dirnames, _ in os.walk(root):
            rel = Path(dirpath).relative_to(root)
            if rel != Path("."):
                if (not dirpath.endswith('raw')):
                    # Clé = minuscule, valeur = chemin réel
                    subdirs[rel.as_posix().lower()] = rel
        return subdirs

    # Regex pour détecter les extensions JPG (case-insensitive)
    JPG_PATTERN = re.compile(r'\.jpe?g$', re.IGNORECASE)

    def has_jpg_files(directory):
        dir_path = Path(directory)
        if not dir_path.is_dir():
            return False
        return any(file.suffix.lower() in {'.jpg', '.jpeg'} for file in dir_path.iterdir() if file.is_file())

    scans_dirs = get_subdirs(scans_root)
    images_dirs = get_subdirs(images_root)

    # Comparaison case-insensitive
    missing_lower = scans_dirs.keys() - images_dirs.keys()

    # Récupérer les chemins réels (ceux de scans/)
    missing = [scans_dirs[lower_key] for lower_key in missing_lower]

    # Trier par chemin relatif (réel, pas lower)
    missing = sorted(missing, key=lambda p: p.as_posix())

    # Construire les URLs pré-remplies
    from django.urls import reverse
    from urllib.parse import quote

    insert_url = reverse('insertnewpictures_form')
    missing_with_url = []
    for rel_path in missing:
        full_path = scans_root / rel_path
        if full_path.is_dir() and has_jpg_files(full_path):
            url = f"{insert_url}?jpegsdirectory={quote(str(full_path))}"
            missing_with_url.append({
                'path': rel_path,
                'full_path': str(full_path),
                'url': url
            })

    context = {
        'missing_dirs': missing_with_url,
        'total': len(missing_with_url)
    }
    return render(request, 'list_missing_scans.html', context)
