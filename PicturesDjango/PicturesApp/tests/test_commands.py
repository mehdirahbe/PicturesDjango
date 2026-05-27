"""
Tests des commandes de management.

Ces tests sont particulièrement importants car les commandes font
beaucoup de travail sur le filesystem et la base.

Stratégie :
- Utiliser TemporaryDirectory
- Mock les parties coûteuses ou dangereuses
- Tester le comportement avec des données contrôlées
"""
from django.test import TestCase
from django.core.management import call_command
from io import StringIO
import tempfile
import os


class ExtractEXIFInfosCommandTest(TestCase):
    """Tests basiques pour la commande ExtractEXIFInfos."""

    def test_command_help(self):
        """Vérifie que la commande s'exécute sans erreur sur --help."""
        from PicturesApp.management.commands.ExtractEXIFInfos import Command as ExtractCommand
        out = StringIO()
        command = ExtractCommand()
        parser = command.create_parser("manage.py", "ExtractEXIFInfos")
        parser.print_help(out)
        output = out.getvalue()
        self.assertIn("Extract EXIF information", output)


# TODO: Ajouter des tests plus poussés avec :
# - Création de fausses images avec EXIF via Pillow en mémoire
# - Vérification que les champs techniques sont bien remplis
# - Tests avec des images sans EXIF
