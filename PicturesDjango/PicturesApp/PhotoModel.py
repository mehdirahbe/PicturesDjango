from django.db import models
import hashlib

'''When models are changed,
Create migrations: Run the following command to create database migrations:
python manage.py makemigrations
Apply migrations: Run the following command to apply the migrations:
python manage.py migrate

'''


# Create your models here.
class PhotoModel(models.Model):
    sujet = models.CharField(max_length=100, db_index=True)
    date = models.CharField(max_length=100)
    #for slides phycally in boxes
    boite = models.CharField(max_length=10, blank=True, null=True, db_index=True)
    rangee = models.IntegerField(null=True)
    numero = models.IntegerField(null=True)
    # specific comment about the picture
    sujet_dias = models.TextField(db_index=True)
    # for slides, if a paper versions exists
    agrandi = models.BooleanField()
    # for slides, don't remember
    classe = models.BooleanField()
    # for slides, don't remember
    verifie = models.BooleanField()
    #generic comment about the place
    commentaire = models.TextField(db_index=True)
    #true is from a digital camera
    camera_digitale = models.BooleanField(db_index=True)
    #directory where pictures are stores, first level
    premier_niveau = models.CharField(max_length=100, db_index=True)
    # directory where pictures are stores, second level
    second_niveau = models.CharField(max_length=100)
    # directory where pictures are stores, third level (may be unused)
    troisieme_niveau = models.CharField(max_length=100, blank=True, null=True)
    nom_fichier_jpeg = models.CharField(max_length=100, blank=True, null=True)
    #primary key in the table
    pkey = models.AutoField(primary_key=True, null=False, db_index=True)
    #md5 hash of the subject, which can easily be passed in an URL
    checksum = models.CharField(max_length=32, db_index=True)

    #save record, overloaded to compute MD5 hash of the subject
    def save(self, *args, **kwargs):
        self.checksum = hashlib.md5(self.sujet.encode(),usedforsecurity=False).hexdigest()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            #Index with more than 1 field
            models.Index(fields=['premier_niveau', 'second_niveau', 'troisieme_niveau']),
            models.Index(fields=['sujet_dias', 'commentaire']),
        ]

    def __str__(self):
        return f"{self.sujet} ({self.date})"
