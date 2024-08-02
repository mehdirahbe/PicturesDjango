from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Photo


def home(request):
    photos = Photo.objects.all()
    return render(request, 'home.html', {'photos': photos})


def search(request):
    query = request.GET.get('q')
    photos = Photo.objects.filter(sujet__icontains=query)
    return render(request, 'search_results.html', {'photos': photos})

def photo_detail(request, photo_id):
    photo = Photo.objects.get(id=photo_id)
    return render(request, 'photo_detail.html', {'photo': photo})
