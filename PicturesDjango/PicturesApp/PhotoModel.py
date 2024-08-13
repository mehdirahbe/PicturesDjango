from django.db import models

'''When models are changed,
Create migrations: Run the following command to create database migrations:
python manage.py makemigrations
Apply migrations: Run the following command to apply the migrations:
python manage.py migrate

'''


# Create your models here.
class PhotoModel(models.Model):
    sujet = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    #for slides phycally in boxes
    boite = models.CharField(max_length=10, blank=True,null=True)
    rangee = models.IntegerField(null=True)
    numero = models.IntegerField(null=True)
    # specific comment about the picture
    sujet_dias = models.TextField()
    # for slides, if a paper versions exists
    agrandi = models.BooleanField()
    # for slides, don't remember
    classe = models.BooleanField()
    # for slides, don't remember
    verifie = models.BooleanField()
    #generic comment about the place
    commentaire = models.TextField()
    #true is from a digital camera
    camera_digitale = models.BooleanField()
    #directory where pictures are stores, first level
    premier_niveau = models.CharField(max_length=100)
    # directory where pictures are stores, second level
    second_niveau = models.CharField(max_length=100)
    # directory where pictures are stores, third level (may be unused)
    troisieme_niveau = models.CharField(max_length=100, blank=True,null=True)
    nom_fichier_jpeg = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.sujet} ({self.date})"
