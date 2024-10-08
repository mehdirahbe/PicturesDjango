from django import forms
import os
from PicturesDjango import settings
from .PhotoModel import PhotoModel
from django.utils.translation import gettext_lazy as _

#Form to ask for a pattern to search. All images having it in comment will then be displayed
class SearchForm(forms.Form):
    search_term = forms.CharField(label=_('Word to search'), max_length=100)

#widget to select a directory
class DirectoryWidget(forms.widgets.Widget):
    #template par défaut de Django pour les champs de texte
    template_name = 'django/forms/widgets/text.html'
    def render(self, name, value, attrs=None, renderer=None):
        if value is not None:
            value = os.path.normpath(value)
        if attrs is None:
            attrs = {}
        attrs['type'] = 'text'
        attrs['webkitdirectory'] = '' #toolkit from chrome to do that
        attrs['directory'] = ''
        return super().render(name, value, attrs, renderer)

    def value_from_datadict(self, data, files, name):
        return data.get(name)

#Form to ask for info about a new serie of images in a subdir of scans
class InsertNewPicturesForm(forms.Form):
    jpegsdirectory = forms.CharField(label=_("JPEGs directory"), widget=DirectoryWidget, max_length=255, help_text=_(
        "Full path to the hard drive folder (scans subdirectory) containing the JPEGs"))
    subject = forms.CharField(label=_("Subject"), max_length=100, help_text=_("Brief description of the subject, must be unique"))
    date = forms.CharField(label=_("Date"), max_length=50, help_text=_("Information about the period"))
    comment = forms.CharField(label=_("Comment"), widget=forms.Textarea, help_text=_("Detailed text"))

    '''Méthodes de Nettoyage : Les méthodes de nettoyage dans Django sont des méthodes de classe dans votre formulaire qui suivent le schéma clean_nom_du_champ. Elles sont utilisées pour effectuer des vérifications ou des transformations supplémentaires sur les données après que les validateurs de base ont été appliqués.
Si une méthode de nettoyage est définie pour un champ (comme clean_jpegsdirectory), elle est appelée après la validation de base du champ.
Si la méthode de nettoyage lève une exception ValidationError, cette erreur est ajoutée aux erreurs du formulaire.
'''
    def clean_jpegsdirectory(self):
        directory = self.cleaned_data['jpegsdirectory']
        if not directory:
            raise forms.ValidationError(_("Please select a folder."))
        if not os.path.isdir(directory):
            raise forms.ValidationError(_("The specified path is not a directory."))
        scansPath = os.path.join(settings.IMAGES_PATH, "scans")
        if not directory.startswith(scansPath):
            raise forms.ValidationError(_(f"The folder must be under {scansPath}"))

        return directory

#to edit sujet_dias when displaying a picture
class PhotoSubjectForm(forms.ModelForm):
    class Meta:
        model = PhotoModel
        fields = ['sujet_dias']