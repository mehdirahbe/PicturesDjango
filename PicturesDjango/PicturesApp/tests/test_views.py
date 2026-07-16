"""
Tests des vues principales.

Stratégie :
- On crée des objets PhotoModel minimaux en mémoire.
- On ne touche jamais aux vraies photos ni au vrai filesystem.
- On utilise la classe de base `PicturesAppTestCase` qui configure automatiquement un IMAGES_PATH temporaire.
"""
from pathlib import Path

from django.test import override_settings
from django.urls import reverse
from django.utils.translation import activate

from PicturesApp.PhotoModel import PhotoModel
from .base import PicturesAppTestCase


class HomeAndLevelViewsTest(PicturesAppTestCase):

    def setUp(self):
        super().setUp()
        activate('en')
        PhotoModel.objects.create(
            sujet="Vacances en Italie",
            date="Été 2024",
            sujet_dias="Superbe photo du Colisée",
            commentaire="Voyage en famille",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="voyages",
            second_niveau="italie_2024",
            nom_fichier_jpeg="001.jpg",
            checksum="test1234567890abcdef1234567890ab",
        )

    def test_home_displays_first_levels(self):
        """La page d'accueil affiche les premier_niveau (dossiers de 1er niveau)."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "voyages")

    def test_home_pagination(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)


class SecondLevelViewsTest(PicturesAppTestCase):

    def setUp(self):
        super().setUp()
        activate('en')
        PhotoModel.objects.create(
            sujet="Vacances en Italie",
            date="Été 2024",
            sujet_dias="Photo de Rome",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="voyages",
            second_niveau="italie_2024",
            nom_fichier_jpeg="001.jpg",
            checksum="abc1234567890abcdef1234567890abc",
        )
        PhotoModel.objects.create(
            sujet="Vacances en Italie",
            date="Été 2024",
            sujet_dias="Photo de Venise",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="voyages",
            second_niveau="italie_2024",
            troisieme_niveau="venise",
            nom_fichier_jpeg="002.jpg",
            checksum="abc1234567890abcdef1234567890abc",
        )

    def test_display_second_level(self):
        response = self.client.get(reverse("DisplaySecondLevel", args=["voyages"]))
        self.assertEqual(response.status_code, 200)
        # Direct series (no third level): subject only
        self.assertContains(response, "Vacances en Italie")
        # Subfolder with third-level series underneath
        self.assertContains(response, "Italie/2024")

    def test_display_third_level(self):
        response = self.client.get(
            reverse("DisplayThirdLevel", args=["voyages", "italie_2024"])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vacances en Italie")


class ContactSheetAndGalleryViewsTest(PicturesAppTestCase):

    def setUp(self):
        super().setUp()
        activate('en')
        self.subject_md5 = "contact1234567890abcdef1234567890a"
        photo = PhotoModel.objects.create(
            sujet="Test Contact Sheet",
            date="2023",
            sujet_dias="Photo principale",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="test",
            second_niveau="contact",
            nom_fichier_jpeg="001.jpg",
            # We pass a placeholder because the model's save() always overwrites checksum from sujet
            checksum="placeholder1234567890abcdef123456",
            appareil="Canon 5D",
        )
        # Force the exact checksum we want to use in the test URLs.
        # Using .update() bypasses the model's save() which always recomputes checksum from sujet.
        PhotoModel.objects.filter(pk=photo.pk).update(checksum=self.subject_md5)

    def test_contacts_sheet(self):
        url = reverse("ContactsSheet", args=[self.subject_md5])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Dans la contact sheet, le seul texte significatif est le sujet de la série (celui de la galerie).
        # On vérifie la présence du checksum dans la page (il apparaît dans le lien vers la galerie).
        self.assertContains(response, self.subject_md5)

    def test_gallery(self):
        import warnings
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            url = reverse("photo_gallery", args=[self.subject_md5])
            # follow=True pour gérer d'éventuelles redirections i18n
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Photo principale")

    def test_contacts_sheet_unknown_subject_returns_200_with_empty_list(self):
        # Unknown checksum: empty queryset and a friendly empty-state message.
        url = reverse("ContactsSheet", args=["nonexistentmd5hash1234567890abcdef"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['photoRecs']), 0)

    def test_gallery_unknown_subject_returns_200_without_crash(self):
        url = reverse("photo_gallery", args=["nonexistentmd5hash1234567890abcdef"])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['photo'])


class LegacySeriesViewsTest(PicturesAppTestCase):
    """Séries héritées : diapos sans arborescence ni JPEG numérisé."""

    def setUp(self):
        super().setUp()
        activate('en')
        self.legacy_md5 = "02118ec40c253cfc4d453d9c67ed15d2"
        for _ in range(3):
            photo = PhotoModel.objects.create(
                sujet="CHAT DEMON ET CHIEN CESAR",
                date="1988-1998",
                sujet_dias="",
                commentaire="",
                agrandi=True,
                classe=False,
                verifie=False,
                camera_digitale=False,
                premier_niveau="",
                second_niveau="",
                nom_fichier_jpeg="",
                checksum="placeholder",
            )
            PhotoModel.objects.filter(pk=photo.pk).update(checksum=self.legacy_md5)

    def test_contacts_sheet_legacy_series_without_jpeg_does_not_crash(self):
        url = reverse("ContactsSheet", args=[self.legacy_md5])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["photoRecs"]), 0)

    def test_photo_detail_legacy_slide_without_nav_does_not_crash(self):
        photo = PhotoModel.objects.filter(checksum=self.legacy_md5).first()
        response = self.client.get(reverse("photoDetail", args=[photo.pkey]))
        self.assertEqual(response.status_code, 200)

    def test_subjects_search_excludes_series_without_viewable_jpeg(self):
        from PicturesApp.views import invalidate_search_cache
        invalidate_search_cache()
        response = self.client.get(reverse("SubjectsBySearch", args=["cesar"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_contacts_sheet_shows_only_scanned_slides(self):
        from PicturesApp.views import invalidate_search_cache
        invalidate_search_cache()
        md5 = "legacyscanned1234567890abcdef12"
        PhotoModel.objects.create(
            sujet="Legacy scanned series",
            date="1990",
            sujet_dias="",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=False,
            premier_niveau="",
            second_niveau="",
            nom_fichier_jpeg="001.jpg",
            checksum="placeholder",
        )
        photo = PhotoModel.objects.filter(sujet="Legacy scanned series").first()
        PhotoModel.objects.filter(pk=photo.pk).update(checksum=md5)
        PhotoModel.objects.create(
            sujet="Legacy scanned series",
            date="1990",
            sujet_dias="",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=False,
            premier_niveau="",
            second_niveau="",
            nom_fichier_jpeg="",
            checksum=md5,
        )
        response = self.client.get(reverse("ContactsSheet", args=[md5]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["photoRecs"]), 1)
        self.assertEqual(response.context["photoRecs"][0].nom_fichier_jpeg, "001.jpg")


class SearchViewsTest(PicturesAppTestCase):

    def setUp(self):
        super().setUp()
        activate('en')
        PhotoModel.objects.create(
            sujet="Vacances Rome",
            date="Ete 2024",
            sujet_dias="Colisee detail",
            commentaire="commentaire bruit",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="voyages",
            second_niveau="italie",
            nom_fichier_jpeg="001.jpg",
            checksum="abc1234567890abcdef1234567890abc",
        )
        PhotoModel.objects.create(
            sujet="Vacances Rome",
            date="Ete 2024",
            sujet_dias="Autre diapo",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="voyages",
            second_niveau="italie",
            troisieme_niveau="rome",
            nom_fichier_jpeg="002.jpg",
            checksum="abc1234567890abcdef1234567890abc",
        )

    def test_search_form_get(self):
        response = self.client.get(reverse("search_form"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "search_term")
        self.assertContains(response, "only_subjects")

    def test_search_post_redirects_to_results(self):
        response = self.client.post(reverse("search_form"), {"search_term": "Rome"})
        self.assertRedirects(response, reverse("ContactsSheetBySearch", args=["Rome"]))

    def test_search_post_only_subjects_redirects(self):
        response = self.client.post(
            reverse("search_form"),
            {"search_term": "Rome", "only_subjects": "on"},
        )
        self.assertRedirects(response, reverse("SubjectsBySearch", args=["Rome"]))

    def test_subjects_by_search_dedupes_and_ignores_commentaire(self):
        response = self.client.get(reverse("SubjectsBySearch", args=["Colisee"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 0)

        response = self.client.get(reverse("SubjectsBySearch", args=["Rome"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.assertContains(response, "Vacances Rome")
        self.assertContains(response, "Voyages / Italie - Vacances Rome")

    def test_subjects_by_search_omits_folder_second_when_no_third_level(self):
        PhotoModel.objects.create(
            sujet="Randonnee Alpes",
            date="2018",
            sujet_dias="",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="voyages",
            second_niveau="alpes",
            nom_fichier_jpeg="010.jpg",
            checksum="aaa11111111111111111111111111111",
        )
        response = self.client.get(reverse("SubjectsBySearch", args=["Alpes"]))
        self.assertContains(response, "Voyages - Randonnee Alpes")
        self.assertNotContains(response, "Voyages / Alpes")

    def test_subjects_by_search_omits_storage_folder_for_direct_series(self):
        PhotoModel.objects.create(
            sujet="Fuerteventura Paques 2013",
            date="2013",
            sujet_dias="",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="voyages",
            second_niveau="fuertepaques2013",
            nom_fichier_jpeg="011.jpg",
            checksum="bbb22222222222222222222222222222",
        )
        response = self.client.get(reverse("SubjectsBySearch", args=["Fuerteventura"]))
        self.assertContains(response, "Voyages - Fuerteventura Paques 2013")
        self.assertNotContains(response, "Fuertepaques2013")

    def test_subjects_by_search_omits_third_level_in_label(self):
        PhotoModel.objects.create(
            sujet="Escapade Venise",
            date="2020",
            sujet_dias="",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="voyages",
            second_niveau="italie",
            troisieme_niveau="venise",
            nom_fichier_jpeg="003.jpg",
            checksum="def4567890abcdef1234567890abcdef",
        )
        response = self.client.get(reverse("SubjectsBySearch", args=["Venise"]))
        self.assertContains(response, "Voyages / Italie - Escapade Venise")
        self.assertNotContains(response, "Venise - Escapade")


class PhotoDetailViewTest(PicturesAppTestCase):

    def setUp(self):
        super().setUp()
        activate('en')
        self.photo = PhotoModel.objects.create(
            sujet="Test technique",
            date="2025",
            sujet_dias="Photo avec données EXIF",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="test",
            second_niveau="exif",
            nom_fichier_jpeg="test.jpg",
            checksum="testexifdata1234567890abcdef12",
            appareil="Sony A7IV",
            focale="85 mm",
            diaphragme="f/1.4",
            temps_pose="1/200 s",
            iso=100,
        )

    def test_photo_detail_displays_technical_data(self):
        """Vérifie que les nouvelles données techniques s'affichent."""
        url = reverse("photoDetail", args=[self.photo.pkey])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sony A7IV")
        self.assertContains(response, "85 mm")
        self.assertContains(response, "f/1.4")
        self.assertContains(response, "1/200 s")
        self.assertContains(response, "ISO: 100")

class PhotoDetail404Test(PicturesAppTestCase):
    """Separate class so we don't run the expensive/fragile setUp just for a 404 test."""

    def setUp(self):
        super().setUp()
        activate('en')

    def test_photo_detail_404_on_unknown_id(self):
        url = reverse("photoDetail", args=[999999])
        # follow=True pour gérer d'éventuelles redirections i18n
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)


class ReadOnlyRemoteTest(PicturesAppTestCase):
    REMOTE_HOST = 'mehdi-thinkbook-13s-g2-itl.taila97662.ts.net'
    LOCAL_HOST = '127.0.0.1'

    def setUp(self):
        super().setUp()
        activate('en')
        self.photo = PhotoModel.objects.create(
            sujet="Read only test",
            date="2025",
            sujet_dias="",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="test",
            second_niveau="readonly",
            nom_fichier_jpeg="photo.jpg",
            checksum="readonly1234567890abcdef1234",
        )

    def test_search_post_allowed_on_remote_host(self):
        response = self.client.post(
            reverse('search_form'),
            {'search_term': 'Rome'},
            HTTP_HOST=self.REMOTE_HOST,
        )
        self.assertRedirects(response, reverse('ContactsSheetBySearch', args=['Rome']))

    def test_subject_edit_blocked_on_remote_host(self):
        response = self.client.post(
            reverse('photoDetail', args=[self.photo.pkey]),
            {'sujet_dias': 'Changed'},
            HTTP_HOST=self.REMOTE_HOST,
        )
        self.assertEqual(response.status_code, 403)

    def test_subject_edit_allowed_on_local_host(self):
        response = self.client.post(
            reverse('photoDetail', args=[self.photo.pkey]),
            {'sujet_dias': 'Changed locally'},
            HTTP_HOST=self.LOCAL_HOST,
        )
        self.assertEqual(response.status_code, 302)
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.sujet_dias, 'Changed locally')

    def test_remote_photo_detail_hides_edit_controls(self):
        response = self.client.get(
            reverse('photoDetail', args=[self.photo.pkey]),
            HTTP_HOST=self.REMOTE_HOST,
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Edit subject')
        self.assertContains(response, 'Share')

    def test_local_photo_detail_shows_edit_controls(self):
        response = self.client.get(
            reverse('photoDetail', args=[self.photo.pkey]),
            HTTP_HOST=self.LOCAL_HOST,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit subject')

    def test_admin_login_blocked_on_remote_host(self):
        response = self.client.get(
            '/en/admin/login/',
            HTTP_HOST=self.REMOTE_HOST,
        )
        self.assertEqual(response.status_code, 404)

    def test_admin_login_allowed_on_local_host(self):
        response = self.client.get(
            '/en/admin/login/',
            HTTP_HOST=self.LOCAL_HOST,
        )
        self.assertEqual(response.status_code, 200)


class ImageRateLimitTest(PicturesAppTestCase):

    def setUp(self):
        super().setUp()
        activate('en')
        self.photo = PhotoModel.objects.create(
            sujet="Rate limit test",
            date="2025",
            sujet_dias="",
            commentaire="",
            agrandi=True,
            classe=False,
            verifie=False,
            camera_digitale=True,
            premier_niveau="test",
            second_niveau="ratelimit",
            nom_fichier_jpeg="thumb.jpg",
            checksum="ratelimit1234567890abcdef1234",
        )
        base = Path(self.images_path) / self.photo.premier_niveau / self.photo.second_niveau
        for size in ('big', 'view', 'contactsheet'):
            target_dir = base / size
            target_dir.mkdir(parents=True, exist_ok=True)
            (target_dir / self.photo.nom_fichier_jpeg).write_bytes(b"fake-jpeg")

    @override_settings(IMAGE_RATE_LIMIT_BIG_VIEW=5, IMAGE_RATE_LIMIT_WINDOW=60)
    def test_big_and_view_share_rate_limit_bucket(self):
        big_url = reverse('photo_Jpeg', args=[self.photo.pkey, 'big'])
        view_url = reverse('photo_Jpeg', args=[self.photo.pkey, 'view'])

        for _ in range(5):
            self.assertEqual(self.client.get(big_url).status_code, 200)

        self.assertEqual(self.client.get(big_url).status_code, 429)
        self.assertEqual(self.client.get(view_url).status_code, 429)

    @override_settings(IMAGE_RATE_LIMIT_BIG_VIEW=5, IMAGE_RATE_LIMIT_WINDOW=60)
    def test_contactsheet_is_not_rate_limited(self):
        url = reverse('photo_Jpeg', args=[self.photo.pkey, 'contactsheet'])

        for _ in range(12):
            self.assertEqual(self.client.get(url).status_code, 200)
