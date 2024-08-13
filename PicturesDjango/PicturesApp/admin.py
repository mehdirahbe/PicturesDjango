from django.contrib import admin

# Register your models here.
from .PhotoModel import PhotoModel

@admin.register(PhotoModel)
class PhotoModelAdmin(admin.ModelAdmin):
    list_display = ('pkey','sujet','date','boite','rangee','numero','sujet_dias','agrandi','commentaire','camera_digitale','premier_niveau','second_niveau','troisieme_niveau','nom_fichier_jpeg')
    search_fields = ('pkey','sujet','date','boite','rangee','numero','sujet_dias','agrandi','commentaire','camera_digitale','premier_niveau','second_niveau','troisieme_niveau')

