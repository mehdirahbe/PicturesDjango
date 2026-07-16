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
from django.db.models import Q, Count, Min, Case, When, Value, IntegerField
from django.conf import settings
from django.urls import reverse
from PicturesDjango.writable_access import reject_readonly_post
from unidecode import unidecode
from rapidfuzz import fuzz
from .forms import SearchForm, InsertNewPicturesForm, PhotoSubjectForm
from .PhotoModel import PhotoModel
from .templatetags.custom_filters import proper_case
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

SEARCH_CACHE_VERSION_KEY = 'search:cache_version'
IMAGE_RATE_LIMIT_CACHE_PREFIX = 'img_rl:big_view'
_RATE_LIMITED_IMAGE_SIZES = frozenset({'big', 'view'})

# Champs interrogés en mode "photos" (recherche classique → planche contact).
PHOTO_SEARCH_FIELDS = ('sujet_dias', 'commentaire', 'lieu', 'date', 'sujet')
# Champs interrogés en mode "sujets uniquement" (date + sujet de série).
SUBJECT_SEARCH_FIELDS = ('date', 'sujet')
RESULT_MODE_PHOTOS = 'photos'
RESULT_MODE_SUBJECTS = 'subjects'

# Mapping champ → filtre SQL icontains (phase 1). Paramétré pour réutiliser la même fuzzy search.
_SEARCH_FIELD_LOOKUPS = {
    'sujet_dias': lambda word: Q(sujet_dias__icontains=word),
    'commentaire': lambda word: Q(commentaire__icontains=word),
    'lieu': lambda word: Q(lieu__icontains=word),
    'date': lambda word: Q(date__icontains=word),
    'sujet': lambda word: Q(sujet__icontains=word),
}

# Diapositive numérisée : agrandi avec un nom de fichier JPEG renseigné.
_VIEWABLE_JPEG_Q = (
    Q(agrandi=True)
    & Q(nom_fichier_jpeg__isnull=False)
    & ~Q(nom_fichier_jpeg='')
)


def _has_nav_level(value):
    return bool(value and str(value).strip())


def _search_base_filter(result_mode):
    """Photos éligibles à la recherche selon le mode."""
    if result_mode == RESULT_MODE_SUBJECTS:
        return _VIEWABLE_JPEG_Q
    return (
        _VIEWABLE_JPEG_Q
        & Q(premier_niveau__isnull=False)
        & ~Q(premier_niveau='')
    )


def _series_checksums_with_viewable_jpeg(checksums):
    if not checksums:
        return set()
    return set(
        PhotoModel.objects.filter(checksum__in=checksums)
        .filter(_VIEWABLE_JPEG_Q)
        .values_list('checksum', flat=True)
        .distinct()
    )


def _filter_photos_to_viewable_series(photos):
    """Mode sujets : ne garder qu'une entrée par série ayant au moins un JPEG."""
    viewable_checksums = _series_checksums_with_viewable_jpeg([photo.checksum for photo in photos])
    seen = set()
    unique = []
    for photo in photos:
        if photo.checksum not in viewable_checksums or photo.checksum in seen:
            continue
        seen.add(photo.checksum)
        unique.append(photo)
    return unique


def _viewable_series_queryset(checksum):
    return PhotoModel.objects.filter(checksum=checksum).filter(_VIEWABLE_JPEG_Q).order_by('pkey')


def _nav_label(value):
    if not value:
        return ''
    return value.replace('_', '/').capitalize()


def _crumb(label, url=None):
    return {'label': label, 'url': url}


def _collections_crumb():
    return _crumb(_('Collections'), reverse('home'))


def _breadcrumbs_home():
    return [_crumb(_('Collections'))]


def _breadcrumbs_search():
    return [
        _collections_crumb(),
        _crumb(_('Search')),
    ]


def _breadcrumbs_search_term(search_term):
    return [
        _collections_crumb(),
        _crumb(_('Search'), reverse('search_form')),
        _crumb(search_term),
    ]


def _breadcrumbs_second_level(first_level):
    return [
        _collections_crumb(),
        _crumb(_nav_label(first_level)),
    ]


def _breadcrumbs_third_level(first_level, second_level):
    return [
        _collections_crumb(),
        _crumb(_nav_label(first_level), reverse('DisplaySecondLevel', args=[first_level])),
        _crumb(_nav_label(second_level)),
    ]


def _breadcrumbs_from_photo(photo, current_label=None):
    label = current_label or proper_case(photo.sujet)
    crumbs = [_collections_crumb()]
    if _has_nav_level(photo.premier_niveau):
        crumbs.append(_crumb(
            _nav_label(photo.premier_niveau),
            reverse('DisplaySecondLevel', args=[photo.premier_niveau]),
        ))
    if (
        photo.troisieme_niveau
        and _has_nav_level(photo.second_niveau)
        and _has_nav_level(photo.premier_niveau)
    ):
        crumbs.append(_crumb(
            _nav_label(photo.second_niveau),
            reverse('DisplayThirdLevel', args=[photo.premier_niveau, photo.second_niveau]),
        ))
    crumbs.append(_crumb(label))
    return crumbs


def _breadcrumbs_photo_detail(photo, series_position=None):
    crumbs = _breadcrumbs_from_photo(photo)[:-1]
    crumbs.append(_crumb(
        proper_case(photo.sujet),
        reverse('ContactsSheet', args=[photo.checksum]),
    ))
    if series_position is not None:
        crumbs.append(_crumb(_('Photo %(position)s') % {'position': series_position}))
    else:
        detail_label = proper_case(photo.sujet_dias) if photo.sujet_dias else _('Photo detail')
        if len(detail_label) > 48:
            detail_label = f'{detail_label[:45]}…'
        crumbs.append(_crumb(detail_label))
    return crumbs


def _breadcrumbs_gallery(photo):
    crumbs = _breadcrumbs_from_photo(photo)[:-1]
    crumbs.append(_crumb(
        proper_case(photo.sujet),
        reverse('ContactsSheet', args=[photo.checksum]),
    ))
    crumbs.append(_crumb(_('Gallery')))
    return crumbs


def _breadcrumbs_search_gallery(search_term, photo):
    crumbs = [
        _collections_crumb(),
        _crumb(_('Search'), reverse('search_form')),
        _crumb(search_term, reverse('ContactsSheetBySearch', args=[search_term])),
    ]
    if photo:
        crumbs.append(_crumb(proper_case(photo.sujet)))
    crumbs.append(_crumb(_('Gallery')))
    return crumbs


def _breadcrumbs_add_pictures():
    return [
        _collections_crumb(),
        _crumb(_('Import')),
    ]


def _breadcrumbs_import():
    return [
        _collections_crumb(),
        _crumb(_('Import'), reverse('list_missing_scans')),
        _crumb(_('New series')),
    ]


def _import_form_context(form):
    return {
        'form': form,
        'breadcrumbs': _breadcrumbs_import(),
        'page_title': _('Import'),
    }


def _search_cache_version():
    return cache.get(SEARCH_CACHE_VERSION_KEY, 0)


def _search_cache_key(normalized, apply_fuzzy, fuzzy_threshold, search_fields, result_mode):
    fields_key = ','.join(search_fields)
    payload = (
        f"{_search_cache_version()}|{normalized}|{int(apply_fuzzy)}|"
        f"{fuzzy_threshold}|{fields_key}|{result_mode}"
    )
    digest = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    return f"search:{digest}"


def _empty_search_result(result_mode):
    return [] if result_mode == RESULT_MODE_SUBJECTS else PhotoModel.objects.none()


def _word_filter_q(word, search_fields):
    word_q = Q()
    for field_name in search_fields:
        word_q |= _SEARCH_FIELD_LOOKUPS[field_name](word)
    return word_q


def _photo_search_tokens(photo, search_fields):
    """Tokenisation phase 2 : mots >= 2 chars, limités aux champs actifs (search_fields)."""
    raw_tokens = set()
    for field_name in search_fields:
        field_value = getattr(photo, field_name, None)
        if field_value:
            for tok in re.split(r'[^a-z0-9]+', str(field_value).lower()):
                if len(tok) >= 2:
                    raw_tokens.add(tok)
    return raw_tokens


def _dedupe_photos_by_checksum(photos):
    """Mode sujets : une entrée par checksum (série), en conservant l'ordre de score."""
    seen = set()
    unique = []
    for photo in photos:
        if photo.checksum in seen:
            continue
        seen.add(photo.checksum)
        unique.append(photo)
    return unique[:1000]


def _photo_to_subject_dict(photo):
    """
    Représentation d'une série pour l'affichage SubjectsBySearch.
    second_niveau sert aussi de dossier disque pour les séries directes (sans 3e niveau).
    On ne l'affiche dans le libellé que si la série a un troisieme_niveau ; dans ce cas,
    on reprend premier/second/troisieme depuis une photo de référence si besoin.
    """
    cover = (
        PhotoModel.objects.filter(checksum=photo.checksum)
        .filter(_VIEWABLE_JPEG_Q)
        .order_by('pkey')
        .first()
    )
    subject = {
        'checksum': photo.checksum,
        'sujet': photo.sujet,
        'cover_id': cover.pkey if cover else None,
        'premier_niveau': photo.premier_niveau,
        'second_niveau': photo.second_niveau,
        'troisieme_niveau': photo.troisieme_niveau or '',
        'date': photo.date,
    }
    if subject['troisieme_niveau']:
        return subject

    ref = (
        PhotoModel.objects.filter(checksum=photo.checksum)
        .exclude(Q(troisieme_niveau__isnull=True) | Q(troisieme_niveau=''))
        .order_by('pkey')
        .first()
    )
    if ref:
        subject['premier_niveau'] = ref.premier_niveau
        subject['second_niveau'] = ref.second_niveau
        subject['troisieme_niveau'] = ref.troisieme_niveau
    return subject


def _photos_to_subject_dicts(photos):
    return [_photo_to_subject_dict(photo) for photo in photos]


def _restore_cached_search(cached_ids, result_mode):
    """Reconstruit le résultat ordonné à partir du cache (pkeys ou checksums selon le mode)."""
    if result_mode == RESULT_MODE_SUBJECTS:
        photos = PhotoModel.objects.filter(checksum__in=cached_ids)
        photo_by_checksum = {photo.checksum: photo for photo in photos}
        ordered_photos = [
            photo_by_checksum[checksum]
            for checksum in cached_ids
            if checksum in photo_by_checksum
        ]
        return _photos_to_subject_dicts(ordered_photos)

    photos = list(PhotoModel.objects.filter(pkey__in=cached_ids))
    photo_dict = {photo.pkey: photo for photo in photos}
    return [photo_dict[pkey] for pkey in cached_ids if pkey in photo_dict]


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


def get_search_queryset(
    search_term,
    apply_fuzzy=True,
    fuzzy_threshold=75,
    search_fields=None,
    result_mode=RESULT_MODE_PHOTOS,
):
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

    Extensions (mode sujets) :
        search_fields limite les champs SQL + tokenisation (ex. date + sujet uniquement).
        result_mode='subjects' déduplique par checksum et retourne des dicts série pour SubjectsBySearch.
    """
    if search_fields is None:
        search_fields = PHOTO_SEARCH_FIELDS
    search_fields = tuple(search_fields)

    if not search_term or not search_term.strip():
        return _empty_search_result(result_mode)

    normalized = unidecode(search_term).lower().strip()
    words = [w for w in normalized.split() if len(w) >= 2]

    cache_key = _search_cache_key(
        normalized, apply_fuzzy, fuzzy_threshold, search_fields, result_mode
    )

    if not words:
        # On met aussi en cache les recherches vides pour éviter des recalculs inutiles
        cache.set(cache_key, [], timeout=900)
        return _empty_search_result(result_mode)

    # ========== CACHE ==========
    # On met en cache la liste des pkeys ou checksums (et non les objets complets) pour éviter
    # de recalculer le scoring fuzzy à chaque affichage de la planche, de la galerie ou des sujets.
    cached_ids = cache.get(cache_key)

    if cached_ids is not None:
        # Reconstruction de la liste ordonnée à partir des identifiants en cache
        return _restore_cached_search(cached_ids, result_mode)

    # ========== PHASE 1 : Récupération LARGE par mot EXACT (union OR) ==========
    # Les records sont trouvés via les mots exacts (david, 2013...). Pas de fuzzy ici.
    base_filter = _search_base_filter(result_mode)

    candidates_qs = PhotoModel.objects.none()

    for word in words:
        candidates_qs |= PhotoModel.objects.filter(
            base_filter & _word_filter_q(word, search_fields)
        )

    # On ramène un pool large (le filtrage dur se fait en phase 2)
    candidates = list(
        candidates_qs.distinct().order_by('pkey')[:3000]
    )

    if not apply_fuzzy:
        if result_mode == RESULT_MODE_SUBJECTS:
            final_photos = _filter_photos_to_viewable_series(_dedupe_photos_by_checksum(candidates))
            cache.set(cache_key, [photo.checksum for photo in final_photos], timeout=900)
            return _photos_to_subject_dicts(final_photos)
        cache.set(cache_key, [photo.pkey for photo in candidates[:1000]], timeout=900)
        return candidates[:1000]

    # ========== PHASE 2 : RÈGLE DURE + scoring hybride ==========
    scored_photos = []
    # Boost sujet_dias uniquement quand ce champ participe à la recherche (mode photos classique)
    use_sujet_dias_boost = 'sujet_dias' in search_fields

    for photo in candidates:
        photo_tokens = _photo_search_tokens(photo, search_fields)

        # Note: on garde les tokens tels quels (david's reste "david's") pour ne pas être trop permissif
        word_scores = []
        exact_in_sujet_dias = 0

        for word in words:
            best_score = 0

            # 1) Match exact sur token ?
            if word in photo_tokens:
                best_score = 100
                # Boost très fort si l'exact match est dans sujet_dias (règle métier)
                if use_sujet_dias_boost and photo.sujet_dias:
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

        # === RÈGLE DURE (Option A stricte) : un seul mot en dessous du seuil → EXCLUSION TOTALE ===
        if min_word_score < fuzzy_threshold:
            # On ne garde pas la photo du tout (c'est la "règle dure pour filtrer")
            continue

        # Score hybride : priorité aux matches exacts + qualité fuzzy + boost sujet_dias
        num_exact = sum(1 for s in word_scores if s >= 99)
        avg_fuzzy = sum(word_scores) / len(word_scores)

        # Base forte pour les matches exacts (chaque mot exact = gros poids)
        base = num_exact * 12
        # Bonus supplémentaire très important pour les matches dans sujet_dias (exigence utilisateur)
        if use_sujet_dias_boost:
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

    if result_mode == RESULT_MODE_SUBJECTS:
        # Limite finale 1000 séries (cohérent avec les autres vues)
        final_photos = _filter_photos_to_viewable_series(
            _dedupe_photos_by_checksum(photo for _, photo in scored_photos)
        )
        cache.set(cache_key, [photo.checksum for photo in final_photos], timeout=900)  # 15 minutes
        return _photos_to_subject_dicts(final_photos)

    # Limite finale 1000 photos (cohérent avec les autres galeries)
    final_results = [photo for _, photo in scored_photos[:1000]]

    # Mise en cache des pkeys (pour éviter de recalculer le fuzzy sur les affichages suivants)
    cache.set(cache_key, [photo.pkey for photo in final_results], timeout=900)  # 15 minutes

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
        denied = reject_readonly_post(request)
        if denied:
            return denied
        form = SearchForm(request.POST)
        if form.is_valid():
            search_term = form.cleaned_data['search_term']
            if form.cleaned_data.get('only_subjects'):
                return redirect('SubjectsBySearch', search_term=search_term)
            return redirect('ContactsSheetBySearch', search_term=search_term)
    else:
        form = SearchForm()
    return render(request, 'search_form.html', {
        'form': form,
        'breadcrumbs': _breadcrumbs_search(),
    })


def home(request):
    """
    Display the home page with first level categories.

    Uses pagination to manage large datasets.

    Also handles the "Copy to smartphone" action via POST.
    """
    if request.method == 'POST' and request.POST.get('action') == 'copy_to_smartphone':
        denied = reject_readonly_post(request)
        if denied:
            return denied
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
        .annotate(
            count=Count('pkey'),
            series_count=Count('checksum', distinct=True),
            cover_id=Min(
                'pkey',
                filter=Q(agrandi=True, nom_fichier_jpeg__isnull=False),
            ),
        )
        .order_by('premier_niveau')
    )
    paginator = Paginator(photo_niveaux, 100)  # Show 100 items per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'breadcrumbs': _breadcrumbs_home(),
    }
    return render(request, 'home.html', context)


def DisplaySecondLevel(request, firstLevel):
    """
    Under a first-level folder: direct photo series (no third level), then
    second-level subfolders that contain third-level series.
    """
    base_qs = PhotoModel.objects.filter(premier_niveau=firstLevel).filter(
        Q(second_niveau__isnull=False) & ~Q(second_niveau='')
    )
    no_third = Q(troisieme_niveau__isnull=True) | Q(troisieme_niveau='')

    direct_series = (
        base_qs.filter(no_third)
        .values('checksum', 'sujet')
        .annotate(
            count=Count('pkey'),
            cover_id=Min(
                'pkey',
                filter=Q(agrandi=True, nom_fichier_jpeg__isnull=False),
            ),
        )
        .order_by('sujet')
    )

    second_folders = (
        base_qs.exclude(no_third)
        .values('second_niveau')
        .annotate(
            count=Count('pkey'),
            series_count=Count('checksum', distinct=True),
            cover_id=Min(
                'pkey',
                filter=Q(agrandi=True, nom_fichier_jpeg__isnull=False),
            ),
        )
        .order_by('second_niveau')
    )

    paginator = Paginator(direct_series, 100)
    page_number = request.GET.get('page')
    direct_series_page = paginator.get_page(page_number)

    context = {
        'firstLevel': firstLevel,
        'direct_series_page': direct_series_page,
        'second_folders': second_folders,
        'breadcrumbs': _breadcrumbs_second_level(firstLevel),
    }
    return render(request, 'secondlevel.html', context)


def DisplayThirdLevel(request, firstLevel, secondLevel):
    """
    Under a first- and second-level folder: photo series that use a third level.
    """
    series = (
        PhotoModel.objects.filter(
            premier_niveau=firstLevel,
            second_niveau=secondLevel,
        )
        .exclude(Q(troisieme_niveau__isnull=True) | Q(troisieme_niveau=''))
        .values('checksum', 'sujet')
        .annotate(
            count=Count('pkey'),
            cover_id=Min(
                'pkey',
                filter=Q(agrandi=True, nom_fichier_jpeg__isnull=False),
            ),
        )
        .order_by('sujet')
    )

    paginator = Paginator(series, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'firstLevel': firstLevel,
        'secondLevel': secondLevel,
        'page_obj': page_obj,
        'breadcrumbs': _breadcrumbs_third_level(firstLevel, secondLevel),
    }
    return render(request, 'thirdlevel.html', context)


def _ensure_session_key(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def _image_rate_limit_cache_key(request):
    return f"{IMAGE_RATE_LIMIT_CACHE_PREFIX}:{_ensure_session_key(request)}"


def _check_big_view_rate_limit(request, size):
    """Session-based quota for big/view JPEGs. contactsheet is exempt."""
    if size not in _RATE_LIMITED_IMAGE_SIZES:
        return None

    limit = getattr(settings, 'IMAGE_RATE_LIMIT_BIG_VIEW', 0)
    window = getattr(settings, 'IMAGE_RATE_LIMIT_WINDOW', 60)
    if limit <= 0:
        return None

    cache_key = _image_rate_limit_cache_key(request)
    count = cache.get(cache_key)
    if count is None:
        cache.set(cache_key, 1, window)
        return None
    if count >= limit:
        logger.warning(
            "Image rate limit exceeded (session=%s, count=%s, limit=%s)",
            request.session.session_key,
            count,
            limit,
        )
        response = HttpResponse(
            _("Too many image requests. Please slow down."),
            status=429,
            content_type="text/plain",
        )
        response["Retry-After"] = str(window)
        return response

    try:
        cache.incr(cache_key)
    except ValueError:
        cache.set(cache_key, 1, window)
    return None


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

    rate_limit_response = _check_big_view_rate_limit(request, size)
    if rate_limit_response is not None:
        return rate_limit_response

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
        denied = reject_readonly_post(request)
        if denied:
            return denied
        form = PhotoSubjectForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path_info)
    else:
        form = PhotoSubjectForm(instance=photo)

    series_qs = _viewable_series_queryset(photo.checksum)
    if series_qs.filter(pkey=photo.pkey).exists():
        previous_photo = series_qs.filter(pkey__lt=photo.pkey).order_by('-pkey').first()
        next_photo = series_qs.filter(pkey__gt=photo.pkey).order_by('pkey').first()
        series_count = series_qs.count()
        series_position = series_qs.filter(pkey__lte=photo.pkey).count()
    else:
        previous_photo = None
        next_photo = None
        series_count = 1
        series_position = 1

    return render(request, 'photo_detail.html', {
        'photoRec': photo,
        'linktogooglemaps': GetLinkToGoogleMaps(photo),
        'subject_form': form,
        'previous_photo': previous_photo,
        'next_photo': next_photo,
        'series_count': series_count,
        'series_position': series_position,
        'breadcrumbs': _breadcrumbs_photo_detail(photo, series_position),
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
    viewable_qs = base_qs.filter(_VIEWABLE_JPEG_Q)
    total_count = viewable_qs.count()
    if total_count > 1000:
        logger.warning(
            "Troncature de la planche contact pour le sujet MD5=%s : %d photos trouvées (>1000), limité à 1000.",
            desiredsubjectMD5, total_count
        )
    allphotos = viewable_qs.order_by('pkey')[:1000]

    if request.method == 'POST' and request.POST.get('action') == 'resize':
        denied = reject_readonly_post(request)
        if denied:
            return denied
        photo = viewable_qs.order_by('pkey').first()
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
        denied = reject_readonly_post(request)
        if denied:
            return denied
        try:
            call_command('AnalyzePhotoQuality', SubjectMD5=desiredsubjectMD5)
            messages.success(request, _("Exposure quality analysis completed for this series."))
        except Exception as e:
            logger.exception("Quality analysis failed for MD5=%s", desiredsubjectMD5)
            messages.error(request, _("Error during analysis: {}").format(e))
        return redirect(f"{request.path_info}?show_quality=1")

    show_quality = request.GET.get('show_quality') == '1'
    worst_photos = _get_worst_exposure_photos(allphotos) if show_quality else []

    first_photo = viewable_qs.order_by('pkey').first() or base_qs.order_by('pkey').first()
    breadcrumbs = _breadcrumbs_from_photo(first_photo) if first_photo else [_crumb(_('Contact sheet'))]

    return render(
        request,
        'contactsSheet.html',
        {
            'photoRecs': allphotos,
            'desiredsubjectMD5': desiredsubjectMD5,
            'worst_photos': worst_photos,
            'total_count': total_count,
            'breadcrumbs': breadcrumbs,
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
    viewable_qs = _viewable_series_queryset(desiredsubjectMD5)
    total_count = viewable_qs.count()
    if total_count > 1000:
        logger.warning(
            "Troncature de la galerie pour le sujet MD5=%s : %d photos trouvées (>1000), limité à 1000.",
            desiredsubjectMD5, total_count
        )
    allphotos = viewable_qs[:1000]
    paginator = Paginator(allphotos, 1)
    page_number = request.GET.get('page')
    photos_page = paginator.get_page(page_number)

    try:
        photo = photos_page[0]
    except (IndexError, TypeError):
        photo = None

    breadcrumbs = _breadcrumbs_gallery(photo) if photo else [_crumb(_('Gallery'))]

    return render(request, 'gallery.html', {
        'photo': photo,
        'photos': photos_page,
        'desiredsubjectMD5': desiredsubjectMD5,
        'linktogooglemaps': GetLinkToGoogleMaps(photo),
        'breadcrumbs': breadcrumbs,
    })


def subjectsBySearch(request, search_term):
    """
    Display photo series (subjects) matching the search term in sujet and date only.
    """
    subjects = get_search_queryset(
        search_term,
        search_fields=SUBJECT_SEARCH_FIELDS,
        result_mode=RESULT_MODE_SUBJECTS,
    )
    paginator = Paginator(subjects, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'subjectsBySearch.html',
        {
            'page_obj': page_obj,
            'search_term': search_term,
            'breadcrumbs': _breadcrumbs_search_term(search_term),
        },
    )


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
    first_photo = allphotos[0] if allphotos else None
    breadcrumbs = _breadcrumbs_search_term(search_term)
    if first_photo:
        breadcrumbs = breadcrumbs[:-1] + [_crumb(proper_case(first_photo.sujet))]
    return render(request, 'contactsSheetBySearch.html', {
        'photoRecs': allphotos,
        'search_term': search_term,
        'breadcrumbs': breadcrumbs,
    })


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

    breadcrumbs = _breadcrumbs_search_gallery(search_term, photo)

    return render(request, 'galleryBySearch.html', {
        'photo': photo,
        'photos': photos_page,
        'search_term': search_term,
        'linktogooglemaps': GetLinkToGoogleMaps(photo),
        'breadcrumbs': breadcrumbs,
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
        denied = reject_readonly_post(request)
        if denied:
            return denied
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
                return render(request, 'InsertNewPictures.html', _import_form_context(form))

            invalidate_search_cache()

            # Generate the MD5 (still needed for the redirect to the contact sheet)
            desiredsubjectMD5 = hashlib.md5(subject.encode(), usedforsecurity=False).hexdigest()

            # Redirect to the contact sheet of the newly imported series
            return redirect('ContactsSheet', desiredsubjectMD5=desiredsubjectMD5)
        else:
            return render(request, 'InsertNewPictures.html', _import_form_context(form))
    else:
        form = InsertNewPicturesForm(initial=initial)

    return render(request, 'InsertNewPictures.html', _import_form_context(form))

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
        'total': len(missing_with_url),
        'breadcrumbs': _breadcrumbs_add_pictures(),
    }
    return render(request, 'list_missing_scans.html', context)
