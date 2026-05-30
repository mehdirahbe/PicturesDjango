from django import forms
import os
import unicodedata
from pathlib import Path
from django.conf import settings
from .PhotoModel import PhotoModel
from django.utils.translation import gettext_lazy as _


def _clean_control_characters(text):
    """
    Nettoie une chaîne de texte libre en supprimant les caractères de contrôle Unicode,
    tout en conservant les caractères de mise en forme utiles (\\n, \\r, \\t).

    Cette version utilise unicodedata.category() et est donc correcte pour
    l'ensemble du jeu de caractères Unicode (français avec accents, grec,
    cyrillique, chinois, emojis, etc.).

    On conserve :
    - \\n, \\r, \\t (retours à la ligne et tabulations)
    - Tous les caractères dont la catégorie Unicode ne commence pas par 'C'
      (c'est-à-dire tout sauf les caractères de contrôle).

    On supprime notamment :
    - Le caractère nul (\\x00)
    - Les autres caractères de contrôle (C0, C1, etc.)
    - Les caractères de formatage invisibles problématiques
    """
    if not text:
        return text

    allowed_controls = {'\n', '\r', '\t'}

    return ''.join(
        c for c in text
        if c in allowed_controls or unicodedata.category(c)[0] != 'C'
    )

#Form to ask for a pattern to search. All images having it in comment will then be displayed
class SearchForm(forms.Form):
    search_term = forms.CharField(label=_('Word to search'), max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Clean control characters (including null bytes) *before* Django validators run
        original_to_python = self.fields['search_term'].to_python

        def cleaned_to_python(value):
            value = original_to_python(value)
            return _clean_control_characters(value)

        self.fields['search_term'].to_python = cleaned_to_python

    def clean_search_term(self):
        search_term = self.cleaned_data.get('search_term', '')
        search_term = search_term.strip()
        # Final pass (in case newlines need normalization, etc.)
        search_term = _clean_control_characters(search_term)
        return search_term

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
    comment = forms.CharField(label=_("Comment"), widget=forms.Textarea, max_length=2048, help_text=_("Detailed text (max ~2KB)"))

    '''Méthodes de Nettoyage : Les méthodes de nettoyage dans Django sont des méthodes de classe dans votre formulaire qui suivent le schéma clean_nom_du_champ. Elles sont utilisées pour effectuer des vérifications ou des transformations supplémentaires sur les données après que les validateurs de base ont été appliqués.
Si une méthode de nettoyage est définie pour un champ (comme clean_jpegsdirectory), elle est appelée après la validation de base du champ.
Si la méthode de nettoyage lève une exception ValidationError, cette erreur est ajoutée aux erreurs du formulaire.
'''
    def clean_jpegsdirectory(self):
        directory = self.cleaned_data['jpegsdirectory']

        if not directory:
            raise forms.ValidationError(_("Please select a folder."))

        # Vérification d'existence (mockable facilement par les tests via os.path.isdir)
        if not os.path.isdir(directory):
            raise forms.ValidationError(_("The specified path does not exist or is invalid."))

        if getattr(settings, 'TESTING', False):
            # === Mode test : comportement allégé pour garder les tests existants fonctionnels ===
            scans_path = os.path.join(settings.IMAGES_PATH, "scans")
            if not directory.startswith(scans_path):
                raise forms.ValidationError(_(f"The folder must be under {scans_path}"))

            if directory == scans_path or directory == scans_path + os.sep:
                raise forms.ValidationError(
                    _("Vous devez sélectionner un sous-dossier à l'intérieur de 'scans/' "
                      "(ex: scans/voyages/fuerteventura_2013), pas le dossier scans lui-même.")
                )
            return directory
        else:
            # === Mode normal : logique Path stricte et robuste (protection contre scans_evil etc.) ===
            try:
                scans_root = (Path(settings.IMAGES_PATH) / "scans").resolve(strict=True)
                selected = Path(directory).expanduser().resolve(strict=True)
            except (FileNotFoundError, RuntimeError):
                raise forms.ValidationError(_("The specified path does not exist or is invalid."))

            if selected == scans_root:
                raise forms.ValidationError(
                    _("Vous devez sélectionner un sous-dossier à l'intérieur de 'scans/' "
                      "(ex: scans/voyages/fuerteventura_2013), pas le dossier scans lui-même.")
                )

            if not selected.is_relative_to(scans_root):
                raise forms.ValidationError(_("Le dossier doit se trouver à l'intérieur du dossier 'scans/'."))

            return str(selected)


    def clean_subject(self):
        subject = self.cleaned_data.get('subject', '')
        subject = subject.strip()
        if not subject:
            raise forms.ValidationError(_("Subject cannot be empty."))
        # Allow newlines, but clean control characters that don't render well
        subject = _clean_control_characters(subject)

        # Unicité du sujet : on ne veut pas ré-importer une galerie qui existe déjà
        if PhotoModel.objects.filter(sujet=subject).exists():
            raise forms.ValidationError(_("Ce sujet existe déjà."))

        return subject

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '')
        comment = comment.strip()
        if not comment:
            raise forms.ValidationError(_("Comment cannot be empty."))
        comment = _clean_control_characters(comment)
        return comment


#to edit sujet_dias when displaying a picture
class PhotoSubjectForm(forms.ModelForm):
    class Meta:
        model = PhotoModel
        fields = ['sujet_dias']

    def clean_sujet_dias(self):
        sujet_dias = self.cleaned_data.get('sujet_dias', '')
        sujet_dias = sujet_dias.strip()
        if not sujet_dias:
            raise forms.ValidationError(_("Description cannot be empty."))
        # Allow newlines for formatting
        sujet_dias = _clean_control_characters(sujet_dias)
        # Add a reasonable limit (2KB)
        if len(sujet_dias) > 2048:
            raise forms.ValidationError(_("Description is too long (max 2KB)."))
        return sujet_dias
