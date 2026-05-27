"""
Classes de base et helpers communs à tous les tests de l'application.

Objectif : centraliser la configuration (override_settings, mocks, etc.)
pour éviter la duplication.
"""
from django.test import TestCase, override_settings
import tempfile
import os


class PicturesAppTestCase(TestCase):
    """
    Classe de base pour les tests qui ont besoin de la base de données.
    Configure automatiquement IMAGES_PATH sur un répertoire temporaire.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._tmp_images_dir = tempfile.TemporaryDirectory()
        cls.images_path = cls._tmp_images_dir.name

    @classmethod
    def tearDownClass(cls):
        cls._tmp_images_dir.cleanup()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.override = override_settings(IMAGES_PATH=self.images_path)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        super().tearDown()


class PicturesAppSimpleTestCase(TestCase):
    """
    Version plus légère (SimpleTestCase) pour les tests qui n'ont pas besoin de DB.
    Utile pour tester les formulaires de manière isolée.
    """

    def setUp(self):
        super().setUp()
        self._tmp_images_dir = tempfile.TemporaryDirectory()
        self.images_path = self._tmp_images_dir.name
        self.override = override_settings(IMAGES_PATH=self.images_path)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        self._tmp_images_dir.cleanup()
        super().tearDown()
