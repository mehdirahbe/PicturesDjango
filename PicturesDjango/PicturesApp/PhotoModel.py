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
    '''
    Règles concernant null et blank (très important pour comprendre ce modèle) :

    • null=True   → La colonne en base de données accepte la valeur NULL.
    • null=False (par défaut) → La colonne est NOT NULL (interdit d’avoir NULL).

    • blank=True  → Le champ peut rester vide dans les formulaires Django (admin, etc.).
    • blank=False (par défaut) → Le champ est obligatoire dans les formulaires.

    Pour les champs texte (CharField, TextField), on préfère généralement
    blank=True plutôt que null=True pour représenter "vide".
    '''

    # === Identification de la galerie / série ===
    # required, subject of the gallery (titre de la série)
    sujet = models.CharField(max_length=100, db_index=True)

    # required, date (as a free text) of the gallery
    date = models.CharField(max_length=100)

    # === Emplacement physique des diapositives (valises de rangement) ===
    # Ces trois champs permettent de localiser physiquement une diapositive
    # dans les valises de classement.
    # - boite   : référence de la valise
    # - rangee  : numéro de la rangée dans la valise (généralement 2 ou 6 rangées)
    # - numero  : position de la diapositive dans la rangée (jusqu'à ~50 par rangée)
    #
    # Ces champs sont NULL tant que la diapositive n'a pas été physiquement
    # classée dans une valise. Ce sont des entiers car ils représentent une
    # position précise dans un système de rangement physique.
    boite = models.CharField(max_length=10, blank=True, null=True, db_index=True)
    # Emplacement physique dans les valises de rangement.
    # Ces champs sont NULL tant que la diapositive n'a pas été classée.
    # rangee = numéro de la rangée (souvent 2 ou 6 rangées par valise)
    # numero = position dans la rangée (jusqu'à ~50 diapos par rangée)
    rangee = models.IntegerField(null=True, blank=True)
    numero = models.IntegerField(null=True, blank=True)

    # === Description de la diapositive ===
    # Commentaire spécifique à la diapositive (souvent appelé "sujet_dias"
    # dans l'ancien programme C++).
    # Ce champ est fréquemment vide pour les anciennes diapositives.
    # Il est donc nullable et peut rester vide dans les formulaires.
    sujet_dias = models.TextField(db_index=True, blank=True, null=True)

    # === Flags historiques liés aux photos papier (tirages physiques) ===
    # Ces champs proviennent de l'ancien programme C++ MFC.
    #
    # camera_digitale :
    #   True  = photo issue d'un appareil numérique
    #   False = scan d'une diapositive argentique (une diapositive physique existe)
    #
    # agrandi :
    #   True si un agrandissement papier a été réalisé à partir de cette diapositive.
    #
    # classe / verifie :
    #   Ces deux flags sont liés au classement et à la vérification des tirages papier.
    #   Ils datent de l'époque où la majorité des photos étaient des agrandissements
    #   physiques. Beaucoup de ces tirages sont encore stockés en vrac dans des boîtes.
    #   Ces informations sont donc souvent incomplètes ou incertaines.
    #   → On autorise explicitement la valeur NULL.
    agrandi = models.BooleanField()
    classe = models.BooleanField(null=True, blank=True)
    verifie = models.BooleanField(null=True, blank=True)
    camera_digitale = models.BooleanField(db_index=True)

    # === Commentaire général de la galerie ===
    # Commentaire générique sur le lieu, le voyage, l'événement, etc.
    # Ce champ est volontairement requis : on ne veut pas de galeries
    # pour lesquelles on n'aurait qu'un titre et une date.
    commentaire = models.TextField(db_index=True)

    # === Hiérarchie de classement des fichiers sur disque ===
    # premier_niveau et second_niveau sont obligatoires.
    # troisieme_niveau est optionnel (beaucoup de séries n'en ont pas).
    premier_niveau = models.CharField(max_length=100, db_index=True)
    second_niveau = models.CharField(max_length=100)
    troisieme_niveau = models.CharField(max_length=100, blank=True, null=True)

    # === Fichier JPEG scanné ===
    # Nom du fichier JPEG. Ce champ est NULL pour les diapositives
    # qui n'ont jamais été scannées (et ne le seront probablement jamais).
    nom_fichier_jpeg = models.CharField(max_length=100, blank=True, null=True)

    # === Clé primaire et identifiant de galerie ===
    pkey = models.AutoField(primary_key=True, db_index=True)
    # MD5 du sujet. Sert d'identifiant stable et court pour les URLs.
    checksum = models.CharField(max_length=32, db_index=True)

    # === Coordonnées GPS (si disponibles) ===
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)

    # === Données techniques EXIF (remplies automatiquement lors de l'import) ===
    appareil = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    focale = models.CharField(max_length=30, blank=True, null=True)
    diaphragme = models.CharField(max_length=20, blank=True, null=True)
    temps_pose = models.CharField(max_length=20, blank=True, null=True)
    iso = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    # Localisation déduite des coordonnées GPS (via Nominatim).
    # Remplie automatiquement. Ne pas confondre avec un sujet_dias
    # écrit manuellement par l'utilisateur.
    lieu = models.CharField(max_length=200, blank=True, null=True, db_index=True)

    # === Exposure analysis (automatic detection of images to improve) ===
    # Populated by the AnalyzePhotoQuality command and the
    # "Analyze exposure quality" button in the contact sheet.
    #
    # luminance_mean : average luminance (0 = pure black, 255 = pure white).
    # shadow_clip_pct / highlight_clip_pct : % of very dark (0-10)
    #   or very bright (245-255) pixels → indicator of lost detail.
    #
    # Goal: identify, *within a given series*, the most problematic photos
    # (too dark or too bright) to retouch in priority.
    luminance_mean = models.FloatField(null=True, blank=True)
    shadow_clip_pct = models.FloatField(null=True, blank=True)
    highlight_clip_pct = models.FloatField(null=True, blank=True)
    quality_analyzed_at = models.DateTimeField(null=True, blank=True)

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
