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
    boite = models.CharField(max_length=10)
    rangee = models.IntegerField()
    numero = models.IntegerField()
    sujet_dias = models.TextField()
    agrandi = models.BooleanField()
    classe = models.BooleanField()
    verifie = models.BooleanField()
    commentaire = models.TextField()
    camera_digitale = models.BooleanField()
    premier_niveau = models.CharField(max_length=100)
    second_niveau = models.CharField(max_length=100)
    troisieme_niveau = models.CharField(max_length=100)
    nom_fichier_jpeg = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.sujet} ({self.date})"
