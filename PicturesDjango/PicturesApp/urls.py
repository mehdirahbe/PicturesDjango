from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('DisplaySecondLevel/<str:firstLevel>', views.DisplaySecondLevel, name='DisplaySecondLevel'),
    path('photo/<int:photo_id>/<str:size>', views.photo_Jpeg, name='photo_Jpeg'),
    path('photoDetail/<int:photo_id>', views.photoDetail, name='photoDetail'),
    #contact sheet and gallery by subject checksum
    path('ContactsSheet/<str:desiredsubjectMD5>', views.contactsSheet, name='ContactsSheet'),
    path('Gallery/<str:desiredsubjectMD5>/', views.Gallery, name='photo_gallery'),
    path('Gallery/<str:desiredsubjectMD5>/page/<int:page>/', views.Gallery, name='photo_gallery'),

    # contact sheet and gallery by search term
    path('ContactsSheetBySearch/<str:search_term>/', views.contactsSheetBySearch, name='ContactsSheetBySearch'),
    path('GalleryBySearch/<str:search_term>/', views.GalleryBySearch, name='photo_galleryBySearch'),
    path('GalleryBySearch/<str:search_term>/page/<int:page>/', views.GalleryBySearch, name='photo_galleryBySearch'),

    #search form
    path('search/', views.search_form, name='search_form'),
]
