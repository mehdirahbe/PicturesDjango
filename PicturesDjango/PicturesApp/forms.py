from django import forms

#Form to ask for a pattern to search. All images having it in comment will then be displayed
class SearchForm(forms.Form):
    search_term = forms.CharField(label='Mot à chercher', max_length=100)

#Form to ask for info about a new serie of images in a subdir of scans
class InsertNewPicturesForm(forms.Form):
    jpegsdirectory = forms.CharField(label="Répertoire des JPEGs", max_length=255, help_text="Chemin complet vers le dossier du disque dur (sous dossier de scans) contenant les JPEG")
    subject = forms.CharField(label="Sujet", max_length=100, help_text="Description courte du sujet")
    date = forms.CharField(label="Date", max_length=50, help_text="Information sur la période")
    comment = forms.CharField(label="Commentaire", widget=forms.Textarea, help_text="Texte détaillé")