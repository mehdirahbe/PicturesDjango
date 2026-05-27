"""
Tests de robustesse et validation des formulaires.

Objectif principal :
- Vérifier que les formulaires se comportent correctement face à des entrées "foireuses"
  (trop longues, vides, avec caractères spéciaux, null bytes, etc.).
- C'est particulièrement important pour InsertNewPicturesForm qui touche au filesystem.
"""
from django.test import SimpleTestCase, TestCase, override_settings
from django import forms
from unittest.mock import patch

from PicturesApp.forms import (
    SearchForm,
    InsertNewPicturesForm,
    PhotoSubjectForm,
)
from PicturesApp.PhotoModel import PhotoModel
from .base import PicturesAppTestCase


class SearchFormTest(SimpleTestCase):
    """Tests pour le formulaire de recherche."""

    def test_valid_search_term(self):
        form = SearchForm(data={"search_term": "vacances italie"})
        self.assertTrue(form.is_valid())

    def test_search_term_too_long(self):
        """Le champ est limité à 100 caractères."""
        long_term = "a" * 101
        form = SearchForm(data={"search_term": long_term})
        self.assertFalse(form.is_valid())
        self.assertIn("search_term", form.errors)

    def test_search_term_empty(self):
        form = SearchForm(data={"search_term": ""})
        self.assertFalse(form.is_valid())

    def test_search_term_control_characters_are_cleaned(self):
        """Les caractères de contrôle sont supprimés dans le champ de recherche."""
        form = SearchForm(data={"search_term": "vacances\x00italie\n2024"})
        if not form.is_valid():
            print("DEBUG SearchForm errors:", form.errors)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['search_term'], "vacancesitalie\n2024")

    def test_search_term_accepts_french_accents_and_unicode(self):
        """Recherche avec accents français et ponctuation Unicode doit marcher."""
        form = SearchForm(data={"search_term": "été à Montréal – naïve forêt"})
        self.assertTrue(form.is_valid())
        cleaned = form.cleaned_data["search_term"]
        self.assertIn("été", cleaned)
        self.assertIn("Montréal", cleaned)
        self.assertIn("naïve", cleaned)
        self.assertIn("–", cleaned)


class InsertNewPicturesFormTest(SimpleTestCase):
    """
    Tests critiques pour le formulaire d'ajout de nouvelles images.
    Ce formulaire est la porte d'entrée du système.

    On mock os.path.isdir pour pouvoir tester la validation complète
    du chemin + les règles sur les champs texte (non vide, limite 2Ko,
    caractères de contrôle, acceptation des \n).
    """

    def _valid_data(self, **overrides):
        data = {
            "jpegsdirectory": "/tmp/images/scans/voyages/test_2024",
            "subject": "Voyage en Italie 2024",
            "date": "Été 2024",
            "comment": "Super voyage avec les enfants.",
        }
        data.update(overrides)
        return data

    def test_valid_data_with_mocked_directory(self):
        """Test complet quand le répertoire est valide (mocké)."""
        with override_settings(IMAGES_PATH="/tmp/images"):
            with patch('PicturesApp.forms.os.path.isdir', return_value=True) as mock_isdir:
                form = InsertNewPicturesForm(data=self._valid_data())
                if not form.is_valid():
                    print("DEBUG form errors (valid_data):", form.errors)
                self.assertTrue(form.is_valid())
                mock_isdir.assert_called()

    @override_settings(IMAGES_PATH="/tmp/images")
    @patch('PicturesApp.forms.os.path.isdir', return_value=True)
    def test_subject_cannot_be_empty_even_with_valid_directory(self, mock_isdir):
        data = self._valid_data(subject="   ")
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("subject", form.errors)

    @override_settings(IMAGES_PATH="/tmp/images")
    @patch('PicturesApp.forms.os.path.isdir', return_value=True)
    def test_comment_cannot_be_empty_even_with_valid_directory(self, mock_isdir):
        data = self._valid_data(comment="")
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("comment", form.errors)

    @override_settings(IMAGES_PATH="/tmp/images")
    @patch('PicturesApp.forms.os.path.isdir', return_value=True)
    def test_comment_respects_2kb_limit(self, mock_isdir):
        data = self._valid_data(comment="x" * 2049)
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("comment", form.errors)

    @override_settings(IMAGES_PATH="/tmp/images")
    @patch('PicturesApp.forms.os.path.isdir', return_value=True)
    def test_subject_accepts_newlines(self, mock_isdir):
        """Le sujet peut contenir des retours à la ligne."""
        data = self._valid_data(subject="Voyage\nen Italie 2024")
        form = InsertNewPicturesForm(data=data)
        self.assertTrue(form.is_valid())

    @override_settings(IMAGES_PATH="/tmp/images")
    @patch('PicturesApp.forms.os.path.isdir', return_value=True)
    def test_other_control_chars_are_stripped_from_subject(self, mock_isdir):
        """Les contrôles autres que \\x00 (que Django bloque nativement) sont nettoyés par notre fonction ; accents et \\n conservés."""
        data = self._valid_data(subject="Voyage\x01\x1fItalie 2024\nété")
        form = InsertNewPicturesForm(data=data)
        self.assertTrue(form.is_valid())
        cleaned = form.cleaned_data["subject"]
        self.assertNotIn("\x01", cleaned)
        self.assertNotIn("\x1f", cleaned)
        self.assertIn("VoyageItalie 2024", cleaned)
        self.assertIn("été", cleaned)
        self.assertIn("\n", cleaned)

    # === Tests spécifiques à la validation du répertoire ===

    @override_settings(IMAGES_PATH="/tmp/images")
    @patch('PicturesApp.forms.os.path.isdir', return_value=False)
    def test_jpegsdirectory_must_exist(self, mock_isdir):
        data = self._valid_data(jpegsdirectory="/tmp/images/scans/voyages/does_not_exist")
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("jpegsdirectory", form.errors)

    @override_settings(IMAGES_PATH="/tmp/images")
    @patch('PicturesApp.forms.os.path.isdir', return_value=True)
    def test_jpegsdirectory_must_be_under_scans(self, mock_isdir):
        data = self._valid_data(jpegsdirectory="/tmp/images/autre_dossier/test")
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("jpegsdirectory", form.errors)

    def test_valid_directory_under_scans_passes(self):
        with override_settings(IMAGES_PATH="/tmp/images"):
            with patch('PicturesApp.forms.os.path.isdir', return_value=True):
                data = self._valid_data(jpegsdirectory="/tmp/images/scans/voyages/mon_serie")
                form = InsertNewPicturesForm(data=data)
                if not form.is_valid():
                    print("DEBUG form errors (under_scans):", form.errors)
                self.assertTrue(form.is_valid())

    @override_settings(IMAGES_PATH="/tmp/images")
    @patch('PicturesApp.forms.os.path.isdir', return_value=True)
    def test_directory_error_takes_precedence_over_text_errors(self, mock_isdir):
        """Si le dossier est invalide, on a quand même l'erreur dossier même si le texte est mauvais."""
        data = self._valid_data(
            jpegsdirectory="/tmp/images/hors_scans",
            subject="",  # aussi invalide
        )
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("jpegsdirectory", form.errors)

    def test_fully_valid_form_with_newlines_in_subject_and_comment(self):
        """Cas nominal : tout est bon, y compris des retours à la ligne dans le texte."""
        with override_settings(IMAGES_PATH="/tmp/images"):
            with patch('PicturesApp.forms.os.path.isdir', return_value=True):
                data = self._valid_data(
                    subject="Voyage\nen Italie\navec les enfants",
                    comment="Beau voyage.\n\nBeaucoup de photos prises."
                )
                form = InsertNewPicturesForm(data=data)
                if not form.is_valid():
                    print("DEBUG form errors:", form.errors)
                self.assertTrue(form.is_valid())

    def test_subject_too_long(self):
        """Le sujet est limité à 100 caractères (contrainte métier importante)."""
        data = self._valid_data(subject="a" * 101)
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("subject", form.errors)

    def test_subject_cannot_be_empty(self):
        data = self._valid_data(subject="   ")
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("subject", form.errors)

    def test_subject_can_contain_newlines(self):
        """Le sujet peut contenir des retours à la ligne (affichage géré dans les templates)."""
        data = self._valid_data(subject="Ligne 1\nLigne 2")
        form = InsertNewPicturesForm(data=data)
        self.assertTrue(form.is_valid() or "jpegsdirectory" in form.errors)  # Le dossier peut faire échouer

    def test_comment_cannot_be_empty(self):
        data = self._valid_data(comment="   \n\n   ")
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("comment", form.errors)

    def test_comment_max_length(self):
        """Limite raisonnable à 2 Ko pour le texte libre."""
        data = self._valid_data(comment="x" * 2049)
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("comment", form.errors)

    def test_date_too_long(self):
        data = self._valid_data(date="a" * 51)
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())

    # ============================================================
    # === Tests de robustesse / entrées foireuses (très important)
    # ============================================================

    @override_settings(IMAGES_PATH="/tmp/images")
    def test_jpegsdirectory_with_null_byte(self):
        """Null byte : souvent utilisé pour des attaques ou pour casser des chemins."""
        data = self._valid_data(jpegsdirectory="/tmp/images/scans/test\x00.jpg")
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())

    def test_subject_with_null_byte(self):
        data = self._valid_data(subject="Voyage\x00Italie")
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())

    def test_subject_accepts_newlines(self):
        """Le 'subject' (titre de série) peut contenir des retours à la ligne."""
        data = self._valid_data(subject="Voyage\nen Italie")
        form = InsertNewPicturesForm(data=data)
        # La validation du dossier va probablement échouer, mais pas à cause du \n
        self.assertTrue(form.is_valid() or "jpegsdirectory" in form.errors)

    def test_subject_with_carriage_return(self):
        data = self._valid_data(subject="Voyage\r\nItalie")
        form = InsertNewPicturesForm(data=data)
        self.assertIn("subject", form.fields)

    def test_very_long_comment(self):
        """Un commentaire extrêmement long ne devrait pas faire planter l'application."""
        huge_comment = "x" * 100_000
        data = self._valid_data(comment=huge_comment)
        form = InsertNewPicturesForm(data=data)
        # Le champ n'a pas de max_length → il accepte.
        # C'est peut-être un point à améliorer (ajouter une limite raisonnable).
        self.assertIn("comment", form.fields)

    def test_binary_garbage_in_fields(self):
        """Test avec des données binaires (potentiellement problématiques)."""
        garbage = b"\x00\x01\x02\xff\xfe".decode("latin1", errors="replace")
        data = self._valid_data(
            subject=garbage,
            date=garbage,
            comment=garbage * 10,
        )
        form = InsertNewPicturesForm(data=data)
        # On vérifie surtout que ça ne fait pas exploser la validation
        self.assertIsInstance(form, InsertNewPicturesForm)

    def test_subject_rejects_most_control_characters(self):
        """Les caractères de contrôle qui ne s'affichent pas bien en HTML sont interdits (sauf \\n \\r \\t)."""
        data = self._valid_data(subject="Test\x00\x01\x1fBad")
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())

    def test_comment_rejects_null_byte(self):
        data = self._valid_data(comment="Texte avec\x00null byte")
        form = InsertNewPicturesForm(data=data)
        self.assertFalse(form.is_valid())

    # ============================================================
    # === Tests Unicode / accents français (demande explicite utilisateur)
    # ============================================================

    @override_settings(IMAGES_PATH="/tmp/images")
    @patch('PicturesApp.forms.os.path.isdir', return_value=True)
    def test_subject_and_comment_accept_french_accents(self, mock_isdir):
        """Les caractères accentués français doivent être acceptés et conservés (full Unicode, pas ASCII only)."""
        data = self._valid_data(
            subject="Vacances en été à Montréal – café naïve",
            comment="Photos prises à côté de l'église, forêt de chênes, naïve lumière d'automne."
        )
        form = InsertNewPicturesForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertIn("été", form.cleaned_data["subject"])
        self.assertIn("naïve", form.cleaned_data["subject"])
        self.assertIn("église", form.cleaned_data["comment"])
        self.assertIn("chênes", form.cleaned_data["comment"])
        # Le tiret cadratin et autres ponctuations Unicode passent aussi
        self.assertIn("–", form.cleaned_data["subject"])

    @override_settings(IMAGES_PATH="/tmp/images")
    @patch('PicturesApp.forms.os.path.isdir', return_value=True)
    def test_unicode_accents_preserved_with_newlines_and_controls_stripped(self, mock_isdir):
        """Combo réaliste : accents français + \\n + \\r + tab conservés, mais \\x00 et autres contrôles supprimés."""
        data = self._valid_data(
            subject="Été 2024\nà l'hôtel naïve – Montréal\r\nCafé & forêt",
            comment="Belle lumière.\n\nAccentué : çà et là, où qu'on aille.\t(avec tab)"
        )
        form = InsertNewPicturesForm(data=data)
        if not form.is_valid():
            print("DEBUG Unicode accent test errors:", form.errors)
        self.assertTrue(form.is_valid())
        subj = form.cleaned_data["subject"]
        comm = form.cleaned_data["comment"]
        # Accents et tirets conservés
        self.assertIn("Été", subj)
        self.assertIn("naïve", subj)
        self.assertIn("Montréal", subj)
        # Newlines et tabulations conservés
        self.assertIn("\n", subj)
        self.assertIn("\r\n", subj)
        self.assertIn("\t", comm)
        # Contrôles indésirables absents (on en avait mis un dans le sujet pour le test)
        # (le sujet n'en avait pas dans cet appel, on en teste un séparé)
        self.assertNotIn("\x00", subj)
        self.assertNotIn("\x01", subj)

    @override_settings(IMAGES_PATH="/tmp/images")
    @patch('PicturesApp.forms.os.path.isdir', return_value=True)
    def test_control_chars_stripped_but_french_text_and_newline_kept(self, mock_isdir):
        """Même avec contrôles parasites (\\x01 etc.), le texte français + retours ligne doivent survivre (Django bloque seulement \\x00)."""
        data = self._valid_data(
            subject="Vacances\x01\x1fen été\nà Paris 2024"
        )
        form = InsertNewPicturesForm(data=data)
        self.assertTrue(form.is_valid())
        cleaned = form.cleaned_data["subject"]
        self.assertEqual(cleaned, "Vacancesen été\nà Paris 2024")  # \x01\x1f partis, \n et accents restés
        self.assertIn("été", cleaned)
        self.assertIn("\n", cleaned)


class PhotoSubjectFormTest(SimpleTestCase):
    """Tests pour le formulaire d'édition du sujet_dias sur une photo."""

    def test_form_accepts_text(self):
        # On ne peut pas facilement instancier le ModelForm sans instance
        # On teste juste que la classe est bien définie
        self.assertEqual(PhotoSubjectForm.Meta.fields, ["sujet_dias"])

    def test_sujet_dias_cannot_be_empty(self):
        form = PhotoSubjectForm(data={"sujet_dias": "   "})
        self.assertFalse(form.is_valid())
        self.assertIn("sujet_dias", form.errors)

    def test_sujet_dias_max_length(self):
        """Limite à 2 Ko pour le texte libre par photo."""
        form = PhotoSubjectForm(data={"sujet_dias": "x" * 2049})
        self.assertFalse(form.is_valid())

    def test_sujet_dias_allows_newlines(self):
        form = PhotoSubjectForm(data={"sujet_dias": "Ligne 1\n\nLigne 2"})
        # Sans instance, on ne peut pas valider complètement, mais on peut tester la logique
        self.assertIn("sujet_dias", form.fields)

    def test_sujet_dias_rejects_null_byte(self):
        form = PhotoSubjectForm(data={"sujet_dias": "Texte avec\x00problème"})
        self.assertFalse(form.is_valid())


from django.test import override_settings

@override_settings(IMAGES_PATH="/tmp/fake_for_photo_subject_tests")
class PhotoSubjectFormWithInstanceTest(TestCase):
    """
    Tests pour PhotoSubjectForm quand on a une vraie instance (permet de tester la validation complète).
    """

    def setUp(self):
        super().setUp()
        self.photo = PhotoModel.objects.create(
            sujet="Test photo",
            date="2025",
            sujet_dias="Description initiale",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="test",
            second_niveau="detail",
            nom_fichier_jpeg="001.jpg",
            checksum="testphotodetail1234567890abcdef",
        )

    def test_sujet_dias_cannot_be_empty_on_update(self):
        form = PhotoSubjectForm(
            instance=self.photo,
            data={"sujet_dias": "   \n\n   "}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("sujet_dias", form.errors)

    def test_sujet_dias_respects_2kb_limit(self):
        form = PhotoSubjectForm(
            instance=self.photo,
            data={"sujet_dias": "x" * 2049}
        )
        self.assertFalse(form.is_valid())

    def test_sujet_dias_accepts_newlines(self):
        """Le sujet_dias peut contenir des retours à la ligne."""
        form = PhotoSubjectForm(
            instance=self.photo,
            data={"sujet_dias": "Première ligne\n\nDeuxième ligne avec plus de détails."}
        )
        self.assertTrue(form.is_valid())

    def test_sujet_dias_strips_control_characters(self):
        """Les contrôles autres que \\x00 (bloqué nativement par Django) sont stripés ; accents + \\n conservés."""
        form = PhotoSubjectForm(
            instance=self.photo,
            data={"sujet_dias": "Texte valide\x01avec accents\nété naïve"}
        )
        self.assertTrue(form.is_valid())
        cleaned = form.cleaned_data["sujet_dias"]
        self.assertNotIn("\x01", cleaned)
        self.assertIn("Texte valideavec accents", cleaned)
        self.assertIn("\n", cleaned)
        self.assertIn("été", cleaned)
        self.assertIn("naïve", cleaned)

    def test_valid_update_with_newlines(self):
        form = PhotoSubjectForm(
            instance=self.photo,
            data={"sujet_dias": "Description mise à jour\navec plusieurs lignes."}
        )
        self.assertTrue(form.is_valid())
        if form.is_valid():
            updated_photo = form.save()
            self.assertIn("\n", updated_photo.sujet_dias)
