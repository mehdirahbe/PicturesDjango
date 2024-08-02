from . import views
from django.urls import path

urlpatterns = [
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('photos/<int:photo_id>', views.photo_detail, name='photo_detail'),
]
