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


def home(request):
    #return render(request, 'test.html')
    photos = PhotoModel.objects.all()
    return render(request, 'home.html', {'photos': photos})


def search(request):
    query = request.GET.get('q')
    photos = PhotoModel.objects.filter(sujet__icontains=query)
    return render(request, 'search_results.html', {'photos': photos})


def photo_Jpeg(request, photo_id, size):
    try:
        photo = PhotoModel.objects.get(pkey=photo_id)
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

def photoDetail(request, photo_id):
    try:
        photo = PhotoModel.objects.get(pkey=photo_id)
        return render(request, 'photo_detail.html', {'photoRec': photo})
    except:
        raise Http404("Record not found")
