"""
Fichier de configuration pour pytest (optionnel).

Même si on utilise pour l'instant django.test.TestCase,
ce fichier permet une migration progressive vers pytest-django.
"""
import pytest

# Exemple d'utilisation future :
# @pytest.fixture
# def sample_photo(db):
#     from PicturesApp.PhotoModel import PhotoModel
#     return PhotoModel.objects.create(...)
