from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('DisplaySecondLevel/<str:firstLevel>', views.DisplaySecondLevel, name='DisplaySecondLevel'),
    path('photo/<int:photo_id>/<str:size>', views.photo_Jpeg, name='photo_Jpeg'),
    path('photoDetail/<int:photo_id>', views.photoDetail, name='photoDetail'),
    path('ContactsSheet/<str:desiredsubjectMD5>', views.contactsSheet, name='ContactsSheet'),
]
