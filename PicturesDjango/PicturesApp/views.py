import hashlib

from django.core.management import call_command
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404
import os
from django.shortcuts import render
from .PhotoModel import PhotoModel
from django.db.models import Q
from django.db.models import Count
from PicturesDjango import settings
from unidecode import unidecode
from .forms import SearchForm, InsertNewPicturesForm

#Return link to google maps if we have coordinates or none
def GetLinkToGoogleMaps(photo):
    if photo is None:
        return None
    if photo.latitude is not None and photo.longitude is not None:
        link="https://www.google.com/maps/search/?api=1&query=" + str(photo.latitude) + ',' + str(photo.longitude)
        return link
    return None


'''Display search form with select word to search in comments'''


def search_form(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_term = form.cleaned_data['search_term']
            return redirect('ContactsSheetBySearch', search_term=search_term)
    else:
        form = SearchForm()
    return render(request, 'search_form.html', {'form': form})


'''Home page, display first level'''


def home(request):
    photo_niveaux = PhotoModel.objects.filter(Q(premier_niveau__isnull=False) & ~Q(premier_niveau='')).values_list(
        'premier_niveau', flat=True).annotate(count=Count('pkey')).order_by(
        'premier_niveau')
    paginator = Paginator(photo_niveaux, 100)  # 100 éléments par page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, 'home.html', context)


'''Display second level (and third if there is one). Links go to the contact sheet to display the related pictures'''


def DisplaySecondLevel(request, firstLevel):
    # Filtrer les enregistrements basés sur le premier niveau
    allphotos = PhotoModel.objects.filter(premier_niveau=firstLevel).filter(
        Q(second_niveau__isnull=False) & ~Q(second_niveau=''))

    # Récupérer les valeurs distinctes du second niveau avec le checksum
    photo_niveaux = (
        allphotos.values_list('second_niveau', 'troisieme_niveau', 'checksum',
                              'sujet')  #order is important, referenced in the html as .0 to .3
        .distinct()
        .annotate(count=Count('pkey'))
        .order_by('sujet')
    )

    # Pagination
    paginator = Paginator(photo_niveaux, 100)  # 100 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, 'secondlevel.html', context)


'''Return an image based on its primary key and the desired size'''


def photo_Jpeg(request, photo_id, size):
    try:
        photo = PhotoModel.objects.get(pkey=photo_id)  #1 record
        #generate path
        Jpegpath = os.path.join(settings.IMAGES_PATH, photo.premier_niveau)
        Jpegpath = os.path.join(Jpegpath, photo.second_niveau)
        if photo.troisieme_niveau:  #not required, can be none
            Jpegpath = os.path.join(Jpegpath, photo.troisieme_niveau)
        Jpegpath = os.path.join(Jpegpath, size)
        Jpegpath = os.path.join(Jpegpath, photo.nom_fichier_jpeg)
        with open(Jpegpath, 'rb') as f:
            image_data = f.read()
        return HttpResponse(image_data, content_type='image/jpeg')
    except:
        raise Http404("Image not found")


'''Return a page with an image based on its primary key. Use big size
Display location/comments related to the image'''


def photoDetail(request, photo_id):
    try:
        photo = PhotoModel.objects.get(pkey=photo_id)  #1 record
        return render(request, 'photo_detail.html', {'photoRec': photo,"linktogooglemaps":GetLinkToGoogleMaps(photo)})
    except:
        raise Http404("Record not found")


'''Displays a contact sheet with all pictures related to a subject, via its MD5.'''

'''Display all pictures with the required subject as  a contact sheet'''


def contactsSheet(request, desiredsubjectMD5):
    try:
        allphotos = PhotoModel.objects.filter(checksum=desiredsubjectMD5).filter(agrandi=True)  #Many records
        return render(request, 'contactsSheet.html', {'photoRecs': allphotos, 'desiredsubjectMD5': desiredsubjectMD5})
    except:
        raise Http404("Subject not found")


'''Display all pictures with the required subject as a gallery'''


def Gallery(request, desiredsubjectMD5):
    try:
        allphotos = PhotoModel.objects.filter(checksum=desiredsubjectMD5).filter(agrandi=True)  #Many records
        paginator = Paginator(allphotos, 1)  # 1 photo par page pour la navigation
        page_number = request.GET.get('page')
        photos_page = paginator.get_page(page_number)

        if photos_page:
            photo = photos_page[0]  # La photo actuelle
        else:
            photo = None  # Si aucune photo n'est trouvée

        return render(request, 'gallery.html', {
            'photo': photo,
            'photos': photos_page,
            'desiredsubjectMD5': desiredsubjectMD5,
             "linktogooglemaps":GetLinkToGoogleMaps(photo)
        })
    except:
        raise Http404("Subject not found")


'''Display all pictures with the search term as  a contact sheet'''


def contactsSheetBySearch(request, search_term):
    try:
        search_term_normalized = unidecode(search_term)
        allphotos = PhotoModel.objects.filter(Q(premier_niveau__isnull=False) & ~Q(premier_niveau='')).filter(
            Q(sujet_dias__icontains=search_term) |
            Q(sujet_dias__icontains=search_term_normalized) |
            Q(commentaire__icontains=search_term) |
            Q(commentaire__icontains=search_term_normalized)).filter(agrandi=True)  #Many records
        return render(request, 'contactsSheetBySearch.html', {'photoRecs': allphotos, 'search_term': search_term})
    except:
        raise Http404("Subject not found")


'''Display all pictures with the search term as a gallery'''


def GalleryBySearch(request, search_term):
    try:
        search_term_normalized = unidecode(search_term)
        allphotos = PhotoModel.objects.filter(Q(premier_niveau__isnull=False) & ~Q(premier_niveau='')).filter(
            Q(sujet_dias__icontains=search_term) |
            Q(sujet_dias__icontains=search_term_normalized) |
            Q(commentaire__icontains=search_term) |
            Q(commentaire__icontains=search_term_normalized)).filter(agrandi=True)  #Many records
        paginator = Paginator(allphotos, 1)  # 1 photo par page pour la navigation
        page_number = request.GET.get('page')
        photos_page = paginator.get_page(page_number)

        if photos_page:
            photo = photos_page[0]  # La photo actuelle
        else:
            photo = None  # Si aucune photo n'est trouvée

        return render(request, 'galleryBySearch.html', {
            'photo': photo,
            'photos': photos_page,
            'search_term': search_term,
            "linktogooglemaps": GetLinkToGoogleMaps(photo)
        })
    except:
        raise Http404("Subject not found")


'''Execute the commands to resize jpegs & add the corresponding entries in the DB'''


def InsertNewPictures(request):
    if request.method == 'POST':
        form = InsertNewPicturesForm(request.POST)
        if form.is_valid():
            # Assumons que vous avez un formulaire qui collecte ces données
            jpegsdirectory = request.POST.get('jpegsdirectory')
            subject = request.POST.get('subject')
            date = request.POST.get('date')
            comment = request.POST.get('comment')

            # Calcul du --seriesdestdirectory
            base_path = os.path.join(settings.IMAGES_PATH, "scans")
            if jpegsdirectory.startswith(base_path):
                seriesdestdirectory = jpegsdirectory[len(base_path):].strip(os.sep)
            else:
                # Gérer le cas où le chemin ne commence pas par le base_path attendu
                raise Http404("Le chemin des jpegs n\'est pas valide.")

            # Add entries related to the jpeg in the DB
            call_command('PrepareEntreesJpegs',
                         jpegsdirectory=jpegsdirectory,
                         subject=subject,
                         date=date,
                         comment=comment)

            # Create big (for screen display) and contactsheet size images
            call_command('ResizeJpegs', seriesdestdirectory=seriesdestdirectory)

            #subject MD5
            desiredsubjectMD5=hashlib.md5(subject.encode(), usedforsecurity=False).hexdigest()

            # Complete DB from EXIF infos
            call_command('ExtractEXIFInfos', SubjectMD5=desiredsubjectMD5)

            # Redirect to the contact sheet of added images
            return redirect('ContactsSheet', desiredsubjectMD5)
        else:
            # Si le formulaire n'est pas valide, on le renvoie avec les erreurs
            return render(request, 'InsertNewPictures.html', {'form': form})
    else:
        # Affichage du formulaire
        return render(request, 'InsertNewPictures.html', {'form': InsertNewPicturesForm()})
