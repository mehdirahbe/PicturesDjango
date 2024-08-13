from django.shortcuts import render

# Create your views here.
import django
from django.db.models import Max, Min, Avg
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.template import loader
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

def photo_detail(request, photo_id):
    photo = PhotoModel.objects.get(id=photo_id)
    return render(request, 'photo_detail.html', {'photo': photo})
