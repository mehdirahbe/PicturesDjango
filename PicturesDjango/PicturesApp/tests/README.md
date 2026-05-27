# Stratégie Globale de Tests - PicturesDjango

## Principes Fondamentaux

1. **Aucun accès aux vraies données**
   - Pas de lecture des vraies photos
   - Pas d'utilisation de la vraie base SQLite en production
   - Toutes les images et chemins sont mockés ou simulés

2. **Pyramide de tests adaptée au projet**
   - **Beaucoup de tests unitaires** sur les formulaires et le modèle (rapides et fiables)
   - **Tests d'intégration** sur les vues (avec mocking des commandes et du FS)
   - **Tests de commandes de management** (avec TemporaryDirectory)
   - Peu ou pas de tests E2E complets (trop lents et fragiles ici)

3. **Focus particulier sur la robustesse**
   - Le projet gère des chemins utilisateurs et des textes libres.
   - Les formulaires sont une surface d'attaque et de bugs potentiels.
   - On teste explicitement les entrées "foireuses".

## Structure Recommandée

```
PicturesApp/tests/
├── __init__.py
├── README.md
├── conftest.py              # (si on passe à pytest plus tard)
├── base.py                  # Classes de base et helpers
├── test_models.py
├── test_forms.py            # ← Priorité haute (robustesse)
├── test_views.py
└── test_commands.py
```

## Priorités de Tests (ordre recommandé)

| Priorité | Domaine                    | Raison                                      | Difficulté |
|----------|---------------------------|---------------------------------------------|------------|
| 1        | Formulaires               | Validation critique + surface utilisateur   | Facile     |
| 2        | Vues de lecture           | Détection de régressions rapides            | Facile     |
| 3        | Vue d'insertion           | Flux métier principal                       | Moyenne    |
| 4        | Modèle PhotoModel         | Logique métier (checksum, nouveaux champs)  | Facile     |
| 5        | Commandes de management   | Outils puissants mais dangereux             | Moyenne    |

## Règles pour les tests

- Utiliser `override_settings(IMAGES_PATH=...)` systématiquement.
- Utiliser `tempfile.TemporaryDirectory()` quand on simule le filesystem.
- Mock `call_command` dans les tests de la vue `InsertNewPictures`.
- Pour les cas "foireux" sur les formulaires : tester les limites de longueur, caractères spéciaux (`\x00`, `\n`, `\r`, très longs strings, etc.).
- Éviter les tests qui dépendent de l'ordre des requêtes sauf si nécessaire.

## Outils recommandés

- `django.test.TestCase` / `SimpleTestCase`
- `unittest.mock`
- `tempfile`
- `django.test.override_settings`
- (Optionnel plus tard) `pytest-django` + `factory-boy`

## Comment exécuter les tests

```bash
cd PicturesDjango
python manage.py test PicturesApp.tests --verbosity=2
```

## Règles métier sur les champs texte libre (subject, commentaire, sujet_dias)

D'après les décisions du projet :

- `subject` et `comment` (dans InsertNewPicturesForm) **ne doivent jamais être vides**.
- `sujet_dias` (PhotoSubjectForm) **ne doit jamais être vide**.
- Une limite raisonnable de **~2 Ko** est appliquée sur les champs de texte libre.
- Les retours à la ligne (`\n`) sont **autorisés** dans `subject`, `comment` et `sujet_dias`.
- La plupart des **caractères de contrôle** qui ne s'affichent pas correctement en HTML sont **interdits** (sauf `\n`, `\r`, `\t`).
- Le null byte (`\x00`) est systématiquement rejeté.

Les templates utilisent `|linebreaksbr` sur `sujet_dias` et `commentaire` pour que les retours à la ligne s'affichent correctement.

Ces règles sont testées dans `test_forms.py`.
