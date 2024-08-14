from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
import django
from django.db.models import Max, Min, Avg
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render
from django.template import loader
import os
from django.shortcuts import render
from .PhotoModel import PhotoModel
from django.db.models import Q
from django.db.models import Count

'''Home page, display first level'''
def home(request):
    photo_niveaux = PhotoModel.objects.filter(Q(premier_niveau__isnull=False) & ~Q(premier_niveau='')).values_list('premier_niveau', flat=True).annotate(count=Count('pkey')).order_by(
        'premier_niveau')
    paginator = Paginator(photo_niveaux, 50)  # 50 éléments par page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, 'home.html', context)
    #return render(request, 'home.html', {'levels': photo_niveaux})

'''Display second level'''
def DisplaySecondLevel(request,firstLevel):
    allphotos = PhotoModel.objects.filter(premier_niveau=firstLevel)  # Many records
    photo_niveaux = allphotos.values_list('second_niveau', flat=True).annotate(count=Count('pkey')).order_by(
        'second_niveau')
    return render(request, 'secondlevel.html', {'levels': photo_niveaux})

def search(request):
    query = request.GET.get('q')
    photos = PhotoModel.objects.filter(sujet__icontains=query)
    return render(request, 'search_results.html', {'photos': photos})


'''Return an image based on its primary key and the desired size'''
def photo_Jpeg(request, photo_id, size):
    try:
        photo = PhotoModel.objects.get(pkey=photo_id)#1 record
        #generate path
        Jpegpath = os.path.join('/home/mehdi/Images', photo.premier_niveau)
        Jpegpath = os.path.join(Jpegpath, photo.second_niveau)
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
        photo = PhotoModel.objects.get(pkey=photo_id)#1 record
        return render(request, 'photo_detail.html', {'photoRec': photo})
    except:
        raise Http404("Record not found")

'''Displays a contact sheet with all pictures related to a subject, via its MD5.'''
def contactsSheet(request, desiredsubjectMD5):
    try:
        allphotos = PhotoModel.objects.filter(checksum=desiredsubjectMD5) #Many records
        return render(request, 'contactsSheet.html', {'photoRecs': allphotos})
    except:
        raise Http404("Subject not found")
