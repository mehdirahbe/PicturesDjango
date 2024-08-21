import hashlib
from django.core.management import call_command
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect
import os
from django.db.models import Q, Count
from PicturesDjango import settings
from unidecode import unidecode
from .forms import SearchForm, InsertNewPicturesForm, PhotoSubjectForm
from .PhotoModel import PhotoModel


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

    Args:
    - request (HttpRequest): The HTTP request object.

    Returns:
    - HttpResponse: Renders the home page with paginated data.
    """
    photo_niveaux = PhotoModel.objects.filter(Q(premier_niveau__isnull=False) & ~Q(premier_niveau='')).values_list(
        'premier_niveau', flat=True).annotate(count=Count('pkey')).order_by('premier_niveau')
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

    Args:
    - request (HttpRequest): The HTTP request object.
    - photo_id (int): The primary key of the photo.
    - size (str): The size of the image to return.

    Returns:
    - HttpResponse: The image data or raises Http404 if not found.
    """
    try:
        photo = PhotoModel.objects.get(pkey=photo_id)
        jpeg_path = os.path.join(settings.IMAGES_PATH, photo.premier_niveau, photo.second_niveau)
        if photo.troisieme_niveau:
            jpeg_path = os.path.join(jpeg_path, photo.troisieme_niveau)
        jpeg_path = os.path.join(jpeg_path, size, photo.nom_fichier_jpeg)

        with open(jpeg_path, 'rb') as f:
            image_data = f.read()
        return HttpResponse(image_data, content_type='image/jpeg')
    except:
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
    photo = PhotoModel.objects.get(pkey=photo_id)
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
    - HttpResponse: Renders the contact sheet or raises Http404 if not found.
    """
    try:
        allphotos = PhotoModel.objects.filter(checksum=desiredsubjectMD5).filter(agrandi=True)
        return render(request, 'contactsSheet.html', {'photoRecs': allphotos, 'desiredsubjectMD5': desiredsubjectMD5})
    except:
        raise Http404("Subject not found")


def Gallery(request, desiredsubjectMD5):
    """
    Display photos in a gallery format for a specific subject.

    Args:
    - request (HttpRequest): The HTTP request object.
    - desiredsubjectMD5 (str): The MD5 checksum of the subject.

    Returns:
    - HttpResponse: Renders the gallery or raises Http404 if not found.
    """
    try:
        allphotos = PhotoModel.objects.filter(checksum=desiredsubjectMD5).filter(agrandi=True)
        paginator = Paginator(allphotos, 1)
        page_number = request.GET.get('page')
        photos_page = paginator.get_page(page_number)

        photo = photos_page[0] if photos_page else None

        return render(request, 'gallery.html', {
            'photo': photo,
            'photos': photos_page,
            'desiredsubjectMD5': desiredsubjectMD5,
            'linktogooglemaps': GetLinkToGoogleMaps(photo)
        })
    except:
        raise Http404("Subject not found")


def contactsSheetBySearch(request, search_term):
    """
    Display a contact sheet of photos matching the search term.

    Args:
    - request (HttpRequest): The HTTP request object.
    - search_term (str): The term to search for.

    Returns:
    - HttpResponse: Renders the search result contact sheet or raises Http404 if not found.
    """
    try:
        search_term_normalized = unidecode(search_term)
        allphotos = PhotoModel.objects.filter(Q(premier_niveau__isnull=False) & ~Q(premier_niveau='')).filter(
            Q(sujet_dias__icontains=search_term) |
            Q(sujet_dias__icontains=search_term_normalized) |
            Q(commentaire__icontains=search_term) |
            Q(commentaire__icontains=search_term_normalized)).filter(agrandi=True)
        return render(request, 'contactsSheetBySearch.html', {'photoRecs': allphotos, 'search_term': search_term})
    except:
        raise Http404("Subject not found")


def GalleryBySearch(request, search_term):
    """
    Display photos in a gallery format matching the search term.

    Args:
    - request (HttpRequest): The HTTP request object.
    - search_term (str): The term to search for.

    Returns:
    - HttpResponse: Renders the search result gallery or raises Http404 if not found.
    """
    try:
        search_term_normalized = unidecode(search_term)
        allphotos = PhotoModel.objects.filter(Q(premier_niveau__isnull=False) & ~Q(premier_niveau='')).filter(
            Q(sujet_dias__icontains=search_term) |
            Q(sujet_dias__icontains=search_term_normalized) |
            Q(commentaire__icontains=search_term) |
            Q(commentaire__icontains=search_term_normalized)).filter(agrandi=True)
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
    except:
        raise Http404("Subject not found")


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
    if request.method == 'POST':
        form = InsertNewPicturesForm(request.POST)
        if form.is_valid():
            jpegsdirectory = request.POST.get('jpegsdirectory')
            subject = request.POST.get('subject')
            date = request.POST.get('date')
            comment = request.POST.get('comment')

            # Calculate the destination directory for series
            base_path = os.path.join(settings.IMAGES_PATH, "scans")
            if jpegsdirectory.startswith(base_path):
                seriesdestdirectory = jpegsdirectory[len(base_path):].strip(os.sep)
            else:
                raise Http404("Le chemin des jpegs n'est pas valide.")

            # Add entries for JPEGs in the DB
            call_command('PrepareEntreesJpegs',
                         jpegsdirectory=jpegsdirectory,
                         subject=subject,
                         date=date,
                         comment=comment)

            # Resize images for screen display and contact sheet
            call_command('ResizeJpegs', seriesdestdirectory=seriesdestdirectory)

            # Generate MD5 for the subject
            desiredsubjectMD5 = hashlib.md5(subject.encode(), usedforsecurity=False).hexdigest()

            # Extract EXIF information
            call_command('ExtractEXIFInfos', SubjectMD5=desiredsubjectMD5)

            # Redirect to the contact sheet of added images
            return redirect('ContactsSheet', desiredsubjectMD5=desiredsubjectMD5)
        else:
            return render(request, 'InsertNewPictures.html', {'form': form})
    else:
        return render(request, 'InsertNewPictures.html', {'form': InsertNewPicturesForm()})