# AGENTS.md — PicturesDjango

Ce fichier est la mémoire du projet. Grok Build le relit depuis la racine git à chaque session. Si la session est perdue, ce document fait foi. Il décrit le code tel qu'il est sur `master`, pas une intention. Le README à la racine est plus ancien et se contredit par endroits (PostgreSQL, `start_django.sh`) : en cas de conflit, croire le code et ce fichier.

Langue du dépôt : mixte. Les chaînes des templates et la plupart des `help` de commandes sont en anglais (traduites en français dans `locale/fr`). Les commentaires, le modèle, les docstrings de recherche et une grande partie du README sont en français. Les réponses à Mehdi se font en français.

## Dépôt

- Racine git : `/home/mehdi/PycharmProjects/PicturesDjango`
- Code Django : sous-dossier `PicturesDjango/` (c'est là que vit `manage.py`)
- Branche de travail : `master`
- Remote : `https://github.com/mehdirahbe/PicturesDjango.git`
- Ne pas force-push. Ne pas changer `git config`.
- Ne committer que les fichiers voulus. `git add .` est dangereux : la racine contient souvent des fichiers non suivis de travail sur les légendes (inventaires JSON, montages JPEG, `voyages_sujets_work/`, `montblanc_sujets_work/`). Ce n'est pas l'application. Ne pas les ajouter, ne pas les supprimer.
- `.idea/`, `.venv/`, `PicturesDjango/staticfiles/` (sauf le readme déjà excepté), `.env` et `*.sqlite3` sont ignorés. Les `.mo` compilés sont versionnés volontairement (commentaire dans `.gitignore`).

`LegacyProgsDoNotUseForDocOnly/` est de l'historique (ancien C++ / scripts). Ne pas s'en servir pour faire évoluer le site. Le code vivant est `PicturesDjango/`.

## À quoi sert le site

Bibliothèque photo personnelle (diapositives argentiques historiques + photos numériques). Une seule app Django, `PicturesApp`, un seul modèle, `PhotoModel`. Pas de comptes visiteurs : la consultation est ouverte. L'écriture n'est autorisée que depuis la machine locale. L'accès distant passe par Tailscale Serve en HTTPS, sans Funnel (le README l'interdit : pas d'authentification forte).

- Public (Tailscale, même compte) : `https://mehdi-thinkbook-13s-g2-itl.taila97662.ts.net/fr/`
- Local : `http://127.0.0.1:8000/fr/`
- Le préfixe de langue fait partie de l'URL. `/` seul ne sert pas le site.

## Arborescence utile

```
PicturesDjango/                  # dépôt git
  AGENTS.md
  README.md                      # partiellement obsolète, voir plus bas
  requirements.txt               # runtime
  requirements-dev.txt           # django-debug-toolbar seulement
  scripts/backup_db.sh
  config/picturesdjango-gunicorn.service
  config/install_gunicorn_service.sh
  config/uninstall_gunicorn_service.sh
  PicturesDjango/                # projet Django (cwd de gunicorn et de manage.py)
    manage.py
    .env                         # gitignoré, à côté de manage.py
    PicturesDjango/              # settings, urls, middleware, wsgi
    PicturesApp/                 # l'unique app
      PhotoModel.py
      views.py
      urls.py
      forms.py
      admin.py
      templatetags/custom_filters.py
      management/commands/
      migrations/                # 0001 … 0008
      tests/
    templates/                   # DIRS du projet, pas dans l'app
    static/                      # sources CSS/JS/images
    staticfiles/                 # collectstatic + WhiteNoise, gitignoré
    locale/fr/LC_MESSAGES/       # django.po + django.mo
```

Il n'y a pas d'autres apps, pas de `signals.py`, pas de `pytest.ini`. Les tests sont `django.test` via `manage.py test`.

## Données hors git

`IMAGES_PATH` vient de `.env` (`python-decouple`), défaut dans le code : `/home/mehdi/Images`. Ne jamais committer ni recopier les valeurs de `.env` (`SECRET_KEY`, chemins réels s'ils diffèrent du défaut).

À côté des images, pas dans le dépôt :

- `IMAGES_PATH/db.sqlite3` — la base. Le README parle encore de configurer PostgreSQL : c'est faux. `settings.DATABASES` est SQLite, fichier posé à côté des images pour que sauvegarde et copie de disque emportent la base avec les JPEG.
- `IMAGES_PATH/scans/<niveau1>/<niveau2>/<niveau3 optionnel>/*.jpg` — originaux à plat dans le dossier de la série. Les sous-dossiers (`raw`, etc.) sont ignorés à l'import et au redimensionnement.
- `IMAGES_PATH/<mêmes niveaux>/big|view|contactsheet/<nom>.jpg` — dérivés servis par le site. Ils ne sont pas sous `scans/`.
- `IMAGES_PATH/smartphone/...` — copie des `big/` pour le téléphone (`copy_images_for_smartphone`).
- `IMAGES_PATH/db-backups/picturesdjango-db-YYYY-MM-DD.sqlite3.zst` — sauvegardes.

Maximum trois niveaux de dossiers sous `scans/` (`PrepareEntreesJpegs` lève une erreur au-delà). Un seul niveau (`scans/un_dossier/` sans second niveau) est accepté à l'import : `second_niveau` est alors `''`. La navigation par dossiers exige un `second_niveau` non vide, donc cette série n'apparaît pas dans l'arbre d'accueil. Elle reste joignable par sa planche (redirection après import) et par la recherche si `premier_niveau` est rempli.

## Lancer, servir, redémarrer

Venv : `.venv` à la racine du dépôt. Dépendances image système listées dans le README (libjpeg, etc.). Pillow du projet est **pillow-simd** (`Pillow-SIMD==9.5.0.post2` dans `requirements.txt`), pas Pillow classique. Ne pas installer les deux en même temps. `requirements-dev.txt` ne contient que `django-debug-toolbar` et ne doit pas être gelé dans `requirements.txt`.

```bash
cd /home/mehdi/PycharmProjects/PicturesDjango
source .venv/bin/activate
# commandes Django depuis le projet, pas depuis la racine git :
cd PicturesDjango
python manage.py migrate
python manage.py collectstatic
python manage.py test
python manage.py runserver
```

`migrate` écrit dans `IMAGES_PATH/db.sqlite3`, pas dans le dépôt.

Production : unité systemd `picturesdjango-gunicorn.service` (fichier source `config/picturesdjango-gunicorn.service`).

- `User`/`Group` : `mehdi`
- `WorkingDirectory` : `.../PicturesDjango/PicturesDjango` (là où est `manage.py`)
- `EnvironmentFile=-.../PicturesDjango/PicturesDjango/.env` (le `-` : un `.env` absent n'empêche pas le démarrage)
- `ExecStart` : `.venv/bin/gunicorn PicturesDjango.wsgi:application --bind 127.0.0.1:8000 --reload --timeout 600 --workers 1`
- `Restart=no` : si on arrête l'unité pour un `runserver`, elle ne revient pas toute seule. `sudo systemctl stop` avant un `runserver` sur le port 8000, puis `restart` pour la remettre.
- Après `network-online.target` et `tailscaled.service`.
- Écoute **uniquement** `127.0.0.1:8000`. Tailscale Serve termine le TLS et proxifie vers ce port. Ne pas binder `0.0.0.0`. Ne pas activer Tailscale Funnel.

`gunicorn --reload` ne recharge que les modules Python. Il ne recharge pas les templates, les `.mo`, ni le manifest WhiteNoise.

Après un changement de **template**, de **settings**, de **traduction** (`compilemessages`) ou de **statique** (y compris `collectstatic`, obligatoire avec WhiteNoise), redémarrer avec exactement :

```bash
sudo systemctl restart picturesdjango-gunicorn.service
```

sudo est sans mot de passe **pour cette commande seulement**. Ne pas l'élargir. Ne pas redémarrer d'autres services.

Installation initiale de l'unité : `config/install_gunicorn_service.sh` (copie vers `/etc/systemd/system/`, `enable`, `restart`). Le README cite encore `./start_django.sh` : ce script n'est plus dans le dépôt.

Un seul worker, timeout 600 s : un import, un `ResizeJpegs` ou un « Prepare for smartphone » lancé depuis le site **bloque l'unique worker** pendant toute l'opération. Le site ne répond plus aux autres requêtes jusqu'à la fin (ou jusqu'au timeout).

## Réglages (`PicturesDjango/settings.py`)

- `DEBUG` : variable d'environnement `DEBUG` valant `true`/`1`/`yes`, sinon la valeur `.env` via decouple, sinon `False`.
- `SECRET_KEY` : `.env` si présente. Sinon repli local dérivé d'`IMAGES_PATH` (pas une clé commitée). Ne pas l'imprimer.
- `TESTING` : vrai si `'test'` est dans `sys.argv`. Assouplit `Path.resolve` dans les formulaires et commandes d'import. Les tests ajoutent aussi l'hôte `testserver` aux hôtes autorisés en écriture.
- `ALLOWED_HOSTS` : `127.0.0.1`, l'IP Tailscale du portable (codée en dur dans settings), et `mehdi-thinkbook-13s-g2-itl.taila97662.ts.net`.
- `CSRF_TRUSTED_ORIGINS` : l'origine HTTPS Tailscale. `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` parce que Django ne voit que du HTTP local derrière Tailscale Serve.
- `WRITABLE_HOSTS` : `127.0.0.1` et `localhost` seulement. L'IP Tailscale est dans `ALLOWED_HOSTS` mais **pas** dans `WRITABLE_HOSTS` : y accéder par l'IP est aussi en lecture seule.
- Pas de réglage `CACHES` : cache Django par défaut, mémoire locale du processus. Avec `--workers 1` c'est cohérent. Passer à plusieurs workers dupliquerait le cache de recherche et le rate-limit.
- `HTML_PAGE_CACHE_SECONDS = 30` (en-tête navigateur, voir middleware).
- `IMAGE_RATE_LIMIT_BIG_VIEW = 20` requêtes `size=big` par session sur `IMAGE_RATE_LIMIT_WINDOW = 5` secondes. `0` désactive. Les tailles `view` et `contactsheet` ne sont pas limitées.
- `LANGUAGE_CODE = 'en-us'`, `LANGUAGES` = en + fr, `USE_I18N = True`, `USE_TZ = True`, `TIME_ZONE = 'UTC'`. Les dates métier ne sont pas des `DateField` : ce sont du texte libre sur `PhotoModel.date`.
- `STATIC_URL = '/static/'`, `STATICFILES_DIRS = PicturesDjango/static`, `STATIC_ROOT = PicturesDjango/staticfiles`, storage `whitenoise.storage.CompressedManifestStaticFilesStorage`. Les noms de fichiers sont hashés au `collectstatic`. Un CSS modifié sans `collectstatic` ne sera pas servi. Après `collectstatic`, redémarrer gunicorn.
- WhiteNoise est juste après `SecurityMiddleware`.
- Debug toolbar : ajouté seulement si `DEBUG` et si le paquet s'importe. Middleware inséré tôt. URL **hors** `i18n_patterns` : `/__debug__/`, pas `/fr/__debug__/`. Store cache, `RESULTS_CACHE_SIZE` 2000. Jamais en production (`DEBUG=False`).
- Au chargement, `settings.py` force un `logging.basicConfig` vers stdout (`[SETTINGS-DEBUG] ...`). Chaque `manage.py` et chaque démarrage gunicorn émet ces lignes. Ce n'est pas un échec de test.

`context_processors.writable_access` expose `allow_writes` aux templates (`True` seulement si l'hôte de la requête est dans `WRITABLE_HOSTS`).

## Modèle `PhotoModel` (`PicturesApp/PhotoModel.py`)

Table unique. Clé primaire explicite : `pkey` (`AutoField`), pas `id`.

Pas de contrainte d'unicité SQL sur `sujet` ni sur `checksum`. L'unicité du sujet est vérifiée dans le formulaire d'import et dans `PrepareEntreesJpegs`. Deux sujets identiques partageraient le même checksum et donc la même galerie.

`save()` recalcule **toujours** `checksum = MD5(sujet)` (`usedforsecurity=False`) avant `super().save()`. Les URL de série (`ContactsSheet`, `Gallery`, …) utilisent ce checksum, pas `pkey`. Renommer `sujet` (admin) change le checksum et casse les liens déjà partagés. `AnalyzePhotoQuality` sauve avec `update_fields` qui n'inclut pas `checksum` : le MD5 est recalculé en mémoire mais pas réécrit, ce qui est sans effet tant que `sujet` ne change pas.

Champs :

| Champ | Rôle |
| --- | --- |
| `sujet` | Titre de série, max 100, indexé. Obligatoire. |
| `date` | Texte libre (période à l'import). `ExtractEXIFInfos` peut le **remplacer** par la date EXIF `jj/mm/aaaa`, photo par photo. |
| `commentaire` | Commentaire de série, obligatoire à l'import, indexé. Même texte copié sur chaque photo de la série. |
| `sujet_dias` | Légende de la diapo. Souvent vide sur l'ancien fonds. Éditable sur la fiche photo. Ne plus y mettre le lieu GPS. |
| `lieu` | Lieu déduit du GPS (Nominatim), max 200. Distinct de `sujet_dias`. |
| `boite`, `rangee`, `numero` | Emplacement physique dans les valises. NULL tant que non classé. À l'import numérique, `boite=''`, `rangee`/`numero` à NULL. |
| `camera_digitale` | `True` = numérique. `False` = scan d'une diapo physique. Indexé. Les imports neufs sont `True`. |
| `agrandi` | Historiquement « tirage papier fait ». Pour le site, une photo affichable doit avoir `agrandi=True` **et** un `nom_fichier_jpeg` non vide. Les imports neufs mettent `agrandi=True`. |
| `classe`, `verifie` | Flags de classement papier, nullable (fonds incomplet). Imports neufs : `False`. |
| `premier_niveau`, `second_niveau`, `troisieme_niveau` | Dossiers disque. Les deux premiers sont prévus comme obligatoires ; `troisieme_niveau` est optionnel (NULL ou `''`). |
| `nom_fichier_jpeg` | Nom de fichier seul, pas un chemin. NULL si la diapo n'a jamais été scannée. |
| `latitude`, `longitude` | Floats, nullable. Lien Google Maps si les deux sont présents. |
| `appareil`, `focale`, `diaphragme`, `temps_pose`, `iso` | EXIF technique, remplis seulement si le champ est encore vide. |
| `luminance_mean`, `shadow_clip_pct`, `highlight_clip_pct`, `quality_analyzed_at` | Analyse d'exposition. NULL tant que `AnalyzePhotoQuality` n'a pas tourné. |

Index composés (migration `0008`) : `(premier_niveau, second_niveau, troisieme_niveau)`, `(sujet_dias, commentaire)`, `(checksum, agrandi)`, `(agrandi, premier_niveau)`.

Admin (`admin.py`) : listage et recherche larges, **tous** les champs éditables. L'admin n'est joignable qu'en local (voir lecture seule). Pas de `createsuperuser` automatique.

Règle d'affichage « JPEG visible » (`_VIEWABLE_JPEG_Q` dans `views.py`) : `agrandi=True`, `nom_fichier_jpeg` non NULL et non `''`. Planches, galeries et recherche s'en servent. Une diapo non scannée ne s'affiche pas ; `photo_Jpeg` répond 404 « No scanned image available for this slide. »

## Carte des URL

`PicturesDjango/urls.py` met **admin + app** dans `i18n_patterns` (préfixe de langue activé, y compris pour la langue par défaut). Il n'y a pas de route sans préfixe pour le site. Les noms ci-dessous sont à préfixer par `/fr/` ou `/en/`.

| Chemin | Nom | Vue |
| --- | --- | --- |
| `` | `home` | Dossiers de premier niveau |
| `DisplaySecondLevel/<firstLevel>` | `DisplaySecondLevel` | Séries directes + sous-dossiers |
| `DisplayThirdLevel/<first>/<second>` | `DisplayThirdLevel` | Séries du troisième niveau |
| `photo/<photo_id>/<size>` | `photo_Jpeg` | JPEG. `size` ∈ `big`, `view`, `contactsheet` |
| `photoDetail/<photo_id>` | `photoDetail` | Fiche, légende, précédent/suivant |
| `ContactsSheet/<md5>` | `ContactsSheet` | Planche de la série |
| `Gallery/<md5>/` | `photo_gallery` | Visionneuse, une photo par page |
| `Gallery/<md5>/page/<page>/` | `photo_gallery` | **Déclaré mais inutilisable** : la vue n'accepte pas l'argument `page` |
| `ContactsSheetBySearch/<terme>/` | `ContactsSheetBySearch` | Planche des photos trouvées |
| `SubjectsBySearch/<terme>/` | `SubjectsBySearch` | Séries trouvées (date + sujet) |
| `GalleryBySearch/<terme>/` | `photo_galleryBySearch` | Visionneuse des résultats |
| `GalleryBySearch/<terme>/page/<page>/` | `photo_galleryBySearch` | Même problème que ci-dessus |
| `search/` | `search_form` | Formulaire. Seul POST autorisé à distance |
| `insertnewpictures/` | `insertnewpictures_form` | Import. Local seulement |
| `missing-scans/` | `list_missing_scans` | Dossiers `scans/` pas encore publiés. Local seulement |
| `admin/` | — | Django admin, dans le préfixe de langue |
| `/__debug__/` | — | Toolbar, seulement si `DEBUG`, **sans** préfixe de langue |

La pagination réelle est la query string `?page=`, générée par `includes/_pagination.html` et par les liens de la visionneuse. Les vues lisent `request.GET.get('page')`. Les routes `.../page/<int:page>/` passeraient `page` en argument à une vue qui ne le déclare pas.

Troncature : planche, galerie et recherche s'arrêtent à **1000** photos (ou 1000 séries en mode sujets). Au-delà, un warning est loggé pour la planche et la galerie de série. L'accueil, le second niveau (séries directes seulement), le troisième niveau et la liste de sujets sont paginés par **100**. Les sous-dossiers du second niveau ne sont pas paginés. La planche de recherche n'est pas paginée (jusqu'à 1000 vignettes d'un coup). La visionneuse pagine par **1**.

Fil d'Ariane : `premier_niveau` / `second_niveau` affichés via `_nav_label` (`_` remplacé par `/`, puis `capitalize`). Le filtre de template `replace_underscore` fait le remplacement seul. `proper_case` ne retouche une chaîne que si plus de la moitié des lettres sont en majuscules (les vieux sujets tout en capitales) ; un mot contenant `'` n'est pas modifié.

## Navigation par dossiers

Accueil : un bloc par `premier_niveau` non vide, avec nombre de photos, nombre de séries (`checksum` distincts) et `cover_id` = plus petit `pkey` avec `agrandi=True` et un nom de JPEG.

Second niveau, pour un `premier_niveau` :

- séries « directes » : `second_niveau` non vide et `troisieme_niveau` NULL ou `''`, groupées par `checksum` + `sujet` ;
- dossiers : lignes qui ont un `troisieme_niveau`, groupées par `second_niveau`.

Troisième niveau : séries avec `troisieme_niveau` non vide, groupées par `checksum` + `sujet`.

Les vignettes de couverture utilisent la taille `contactsheet` via `photo_Jpeg`. `lazysizes` est chargé dans `base.html`.

## Servir un JPEG (`photo_Jpeg`)

Chemin construit, pas stocké :

```
IMAGES_PATH / premier_niveau / second_niveau [/ troisieme_niveau] / <size> / nom_fichier_jpeg
```

`FileResponse` en `image/jpeg`. 404 si taille inconnue, photo inconnue, `nom_fichier_jpeg` vide, ou fichier absent. Toute autre exception est loggée puis devient 404.

Rate-limit **uniquement** `size=big` : compteur de session `img_rl:big:<session_key>`, 20 par 5 secondes. Dépassement : HTTP 429, corps texte, `Retry-After` = la fenêtre. La première image `big` crée la session si besoin. Les vignettes de navigation ne comptent pas, la visionneuse oui (elle affiche `big`).

## Pipeline d'import

Point d'entrée recommandé : commande `ImportSeries`, appelée aussi par la vue `InsertNewPictures`.

Ordre dans `ImportSeries` :

1. Le dossier doit exister, être **strictement sous** `IMAGES_PATH/scans` (`Path.resolve` + `is_relative_to`), et ne pas être `scans/` lui-même. Le chemin relatif après `scans/` devient `seriesdestdirectory`.
2. **`ResizeJpegs` hors transaction.** Échec d'une image : la commande lève, aucune écriture SQL (la transaction n'a pas commencé). Les JPEG déjà écrits par les workers précédents restent sur disque.
3. Transaction atomique : `PrepareEntreesJpegs` puis `ExtractEXIFInfos --SubjectMD5 <md5 du sujet>`. Si l'EXIF lève, les `PhotoModel` sont annulés, mais les fichiers redimensionnés restent.
4. La vue, en cas de succès, appelle `invalidate_search_cache()` puis redirige vers `ContactsSheet`.

`ResizeJpegs` :

- Accepte un chemin relatif après `scans/` ou un chemin absolu qui doit être sous `scans/`. Refuse `..`.
- Ne lit que les `.jpg`/`.jpeg` **directement** dans le dossier source (pas les sous-dossiers).
- Crée `IMAGES_PATH/<relatif>/{big,view,contactsheet}/`.
- Intelligent : ne régénère que si une cible manque, est illisible (`Image.verify()`), ou si la source est plus récente (retouche).
- Progression : orientation EXIF appliquée et **jetée** (les dérivés sont déjà tournés), conversion RGB, Lanczos. `big` = plus grand côté 1935, qualité JPEG 93 ; `view` = moitié (967), qualité 89, calculé depuis `big` en mémoire ; `contactsheet` = 1935//10 = 193, qualité 87, calculé depuis `view`.
- `ProcessPoolExecutor`, `cpu_count - 1` workers. Un échec arrête tout (`future.result()` puis `raise`).
- Pillow-SIMD est détecté si la version contient `post`.

`PrepareEntreesJpegs` crée une ligne par JPEG trié par nom : `agrandi=True`, `camera_digitale=True`, `classe=False`, `verifie=False`, `sujet_dias=''`, `boite=''`, niveaux pris sur les composantes du chemin relatif (1 à 3). Refuse un sujet déjà présent. Annonce les sous-dossiers ignorés.

Bouton « resize » sur la planche (POST `action=resize`, local seulement) relance **seulement** `ResizeJpegs`, pas l'EXIF ni l'analyse.

Repérer un dossier pas encore importé : `list_missing_scans` (GET, local seulement, sinon 404). Compare les sous-dossiers de `scans/` à ceux d'`IMAGES_PATH` (clés en minuscules). Ignore tout chemin qui **se termine** par la chaîne `raw` (donc un dossier nommé `raw`, mais aussi un nom qui finit par `raw`). Ne liste que les dossiers qui contiennent des JPEG directement. Chaque ligne ouvre `insertnewpictures/?jpegsdirectory=<chemin complet>`.

Formulaire `InsertNewPicturesForm` : sujet, date et commentaire obligatoires ; sujet unique ; caractères de contrôle Unicode retirés (`\n`, `\r`, `\t` gardés) ; commentaire max 2048. En test, le contrôle de chemin est un `startswith` sur `IMAGES_PATH/scans` (moins strict). Hors test, `resolve(strict=True)` et `is_relative_to`. `PhotoSubjectForm` : `sujet_dias` obligatoire, mêmes nettoyages, max 2048. Les templates passent `sujet_dias` et `commentaire` par `linebreaksbr`.

## EXIF, GPS, lieu (`ExtractEXIFInfos`)

Lit l'**original** sous `scans/`, pas le dérivé `big/`. Sans `--SubjectMD5`, parcourt toutes les photos `agrandi=True` avec un nom de JPEG et un `premier_niveau`. Avec `--SubjectMD5`, filtre le checksum et `agrandi=True` (l'import vient de créer ces lignes).

Pour chaque photo, si l'EXIF se lit :

- `DateTimeOriginal` → `date` en `%d/%m/%Y` **si différent** de la valeur actuelle. Le texte de période saisi à l'import est donc écrasé dès qu'une date de prise de vue existe. C'est par photo, plus par série.
- Champs techniques (`appareil`, `focale`, `diaphragme`, `temps_pose`, `iso`) : extraits seulement si au moins un est vide, et chaque champ n'est écrit que s'il est vide. Pas d'écrasement d'une valeur déjà là.
  - Appareil : `Make` + `Model`, marque nettoyée, pas de doublon « Samsung Samsung … ».
  - Diaphragme : `FNumber`, sinon `ApertureValue` APEX.
  - Pose : `ExposureTime`, sinon `ShutterSpeedValue` APEX.
  - ISO : `ISOSpeedRatings` (scalaire ou premier élément d'un tuple).
- GPS : `GPSInfo` tags 1–4, conversion degrés/minutes/secondes, sud et ouest négatifs. Coordonnées écrites **seulement si `longitude` est NULL** (les deux champs ensemble).
- `lieu` : si vide et coordonnées présentes. Cache local arrondi `(int(lat*100), int(lon*100))` combiné en un entier. Sinon Nominatim `reverse`, `zoom=12`, `language=fr`, User-Agent `PicturesDjango/1.1`, timeout 10 s, **`time.sleep(1.1)` entre appels**, **plafond 99 appels par exécution** (le compteur s'arrête avant 100). Au-delà, la photo garde des coordonnées sans lieu. `build_short_location` produit un texte court (village/ville, puis county/state, puis pays). Le résultat n'est **pas** écrit dans `sujet_dias`.

Les erreurs par image sont imprimées et n'arrêtent pas la boucle. `photo.save()` complet (donc recalcul du checksum).

`MigrateOldGpsToLieu` est **dépréciée** : `handle()` affiche une erreur et `return` immédiatement. Le code en dessous est mort (il déplaçait d'anciens libellés GPS de `sujet_dias` vers `lieu`). Ne pas le réactiver.

`FillFromLegacyCppDb` est **dépréciée** de la même façon (import one-shot de l'ancienne base binaire C++ MFC des années 90, `Dias.bdd`, chaînes C terminées par NUL, encodage ISO-8859-1 / batches `preparehtml.bat` en cp1252). Ne jamais la relancer : des centaines de photos ont été ajoutées depuis.

## Qualité d'exposition (`AnalyzePhotoQuality`)

Bouton sur la planche (POST `action=analyze_quality`, local) ou :

```bash
python manage.py AnalyzePhotoQuality --SubjectMD5 <md5>
python manage.py AnalyzePhotoQuality            # toute la base, lent
python manage.py AnalyzePhotoQuality --force    # réanalyse même si quality_analyzed_at est rempli
```

Choisit le plus petit fichier existant parmi `contactsheet`, `view`, `big`, sinon l'original dans `scans/`. Réduit à 600 px, luminance moyenne 0–255, % de pixels 0–10 (ombres) et 245–255 (hautes lumières). Pillow seul, pas numpy. Ignore les photos déjà datées sauf `--force`.

La planche n'affiche les « pires » que si `?show_quality=1` (le bouton redirige avec cette query). Score dans `_get_worst_exposure_photos` : `0.65 * |luminance-128|/128 + 0.35 * max(clip)/100`, top 5. Les photos sans métrique sont ignorées.

## Recherche (`get_search_queryset`)

`SearchForm` : champ `search_term` (max 100, nettoyé) et case `only_subjects`. POST valide → redirection vers `SubjectsBySearch` ou `ContactsSheetBySearch`. Ce POST est le seul autorisé depuis un hôte distant (`READONLY_SAFE_POST_URL_NAMES`).

Deux modes :

- photos (défaut) : champs `sujet_dias`, `commentaire`, `lieu`, `date`, `sujet`. Base : JPEG visible **et** `premier_niveau` non vide. Résultat : liste de `PhotoModel` (max 1000), ordre de score.
- sujets (`only_subjects`) : champs `date` et `sujet` seulement. Base : JPEG visible, sans exiger `premier_niveau` à la phase SQL, puis on ne garde que les séries qui ont au moins un JPEG visible. Une entrée par checksum. Dicts avec couverture, niveaux, date. Le libellé de dossier n'affiche `second_niveau` que s'il existe un `troisieme_niveau` quelque part dans la série.

Algorithme (docstring « option A ») :

1. `unidecode`, minuscules, mots de longueur ≥ 2. Requête vide → liste vide, quand même mise en cache.
2. Phase 1 : pour chaque mot, `icontains` en OR sur les champs du mode, union, `distinct`, max **3000** candidats triés par `pkey`. Pas de fuzzy ici.
3. Si `apply_fuzzy=False` (l'UI ne le coupe pas ; défaut `True`) : pas de phase 2.
4. Phase 2, seuil `fuzzy_threshold=75` : pour chaque mot, score 100 si le token exact est présent ; si le mot est une année (`isdigit`), **pas de fuzzy**, il faut l'exact ; sinon `rapidfuzz.fuzz.WRatio` sur les tokens du champ, en ignorant les tokens plus courts que `max(3, len(mot)-2)`. **Un seul mot sous 75 élimine la photo.** Score hybride : +12 par mot exact, +18 si l'exact est dans `sujet_dias` (mode photos seulement), + moyenne et pire score. Plancher `final_score < 12` élimine encore. Tri décroissant.

Cache : clé SHA-256 de (version, requête, fuzzy, seuil, champs, mode). Valeur : `pkey` ou checksums, **15 minutes** (`timeout=900`). Version globale `search:cache_version`, incrémentée **uniquement** par `invalidate_search_cache()` après un import réussi. Modifier une légende (`photoDetail`) ou lancer l'EXIF **ne invalide pas** le cache : la recherche peut rester fausse jusqu'à 15 minutes, ou jusqu'au prochain import. Le cache est en mémoire du worker.

## Lecture seule, auth, accès distant

Il n'y a pas de login pour la galerie. `django.contrib.auth` sert à l'admin.

`ReadOnlyRemoteMiddleware` (après CSRF, avant `AuthenticationMiddleware`) :

1. Si l'hôte n'est pas inscriptible et que le chemin contient `/admin` → **404** (pas 403), avec un warning.
2. Si l'hôte n'est pas inscriptible et que le `url_name` n'est pas dans `READONLY_ALLOWED_URL_NAMES` → **404**. Donc `insertnewpictures` et `missing-scans` sont invisibles à distance, même en GET. Un 404 de résolution Django est laissé passer (`Resolver404` → `None`).
3. POST/PUT/PATCH/DELETE depuis un hôte non inscriptible, sauf `search_form` → **403** texte « Write operations are only allowed from the local server. »

Liste blanche de noms d'URL distants : `home`, `DisplaySecondLevel`, `DisplayThirdLevel`, `photo_Jpeg`, `photoDetail`, `ContactsSheet`, `photo_gallery`, `ContactsSheetBySearch`, `SubjectsBySearch`, `photo_galleryBySearch`, `search_form`.

Les templates cachent en plus, via `allow_writes`, l'import, la copie smartphone, l'édition de `sujet_dias`, et les boutons resize / analyse. Le middleware reste la barrière réelle.

Écritures locales :

- accueil POST `action=copy_to_smartphone` → `copy_images_for_smartphone` ;
- planche POST `resize` ou `analyze_quality` ;
- fiche POST → `PhotoSubjectForm` sur `sujet_dias` ;
- import POST → `ImportSeries`.

`ShortHtmlCacheMiddleware` (en dernier) : sur GET/HEAD, status 200, `Content-Type` commençant par `text/html`, sans `Cache-Control` déjà posé, ajoute `Cache-Control: max-age=30, private`. Les JPEG ne sont pas concernés. Un changement de légende peut donc mettre jusqu'à 30 s à apparaître dans le navigateur, en plus du cache de recherche.

## Internationalisation

Chaînes sources en anglais dans les templates (`{% trans %}` / `{% load i18n %}`) et dans une partie du Python (`gettext`). Traduction française : `PicturesDjango/locale/fr/LC_MESSAGES/django.po`, compilée dans `django.mo` (versionné).

```bash
cd PicturesDjango
python manage.py makemessages --locale fr    # paquet Debian gettext requis
# éditer django.po
python manage.py compilemessages
sudo systemctl restart picturesdjango-gunicorn.service
```

`LocaleMiddleware` est après `SessionMiddleware` et avant `CommonMiddleware`, comme l'exige Django. La langue active vient du préfixe d'URL. Il n'y a **pas** de sélecteur de langue dans `base.html` : les liens `{% url %}` restent dans la langue courante. L'usage normal est `/fr/`. `LANGUAGE_CODE` est `en-us`, donc une URL `/en/` affiche les msgid anglais.

Le `.po` a encore l'en-tête fuzzy d'origine ; les `msgstr` français, eux, sont remplis. Après édition, sans `compilemessages`, rien ne change. Sans redémarrage de gunicorn, le `.mo` déjà chargé peut rester en mémoire.

## Templates, statique, JavaScript

Templates du projet (`TEMPLATES['DIRS']`) : `base.html` (thème sombre Bootstrap, logo `static/img/logo.png`, barre d'outils), `home.html`, `secondlevel.html`, `thirdlevel.html`, `contactsSheet.html`, `contactsSheetBySearch.html`, `subjectsBySearch.html`, `gallery.html`, `galleryBySearch.html`, `photo_detail.html`, `search_form.html`, `InsertNewPictures.html`, `list_missing_scans.html`, et `templates/includes/` (fil d'Ariane, pagination, vignette, métadonnées, EXIF, partage, bouton lecture, ligne de recherche de sujet).

`static/` : `bootstrap.min.css`, `bootstrap.bundle.min.js`, `lazysizes.min.js`, `css/custom.css`, `js/app.js`, `img/logo.png`. Le README dit encore « changer le look dans base.html » : le CSS vivant est `static/css/custom.css`, puis `collectstatic`.

`app.js` :

- filtre client sur `[data-filter-input]` (normalisation NFD, sans accent) ;
- densité des grilles, mémorisée dans `localStorage` clé `pictures-density` ;
- visionneuse : intervalle **5000 ms** (`data-gallery-interval` sur `gallery.html` et `galleryBySearch.html`). Flèches gauche/droite, Espace lecture/pause, Échap stoppe, `i` panneau d'infos. Le paramètre `?play=1` est posé dans l'URL pour que la lecture survive au changement de page. En fin de série, le lien « suivant » absent fait revenir à la première page. Préfetch de la page suivante. Le bouton est désactivé s'il n'y a qu'une photo ;
- partage : en HTTP, le `<a target="_blank">` ouvre le JPEG `big`. En contexte sûr (HTTPS Tailscale) **et** si `navigator.share` existe, le clic est intercepté : partage du fichier si déjà préchargé, sinon partage de l'URL, sinon ouverture d'un onglet. Le prefetch télécharge le `big` (donc compte dans le rate-limit).

Pas de framework JS. Pas de `node_modules`.

## Commandes de management

Toutes sous `PicturesApp/management/commands/`, à lancer depuis `PicturesDjango/` avec le venv.

| Commande | État | Rôle |
| --- | --- | --- |
| `ImportSeries` | à utiliser | Orchestre resize puis Prepare + EXIF |
| `ResizeJpegs` | à utiliser | Dérivés big/view/contactsheet |
| `PrepareEntreesJpegs` | via ImportSeries | Crée les lignes |
| `ExtractEXIFInfos` | via ImportSeries, ou backfill | Date, GPS, lieu, technique |
| `AnalyzePhotoQuality` | à utiliser | Métriques d'exposition |
| `copy_images_for_smartphone` | à utiliser | Copie `big/` vers `IMAGES_PATH/smartphone/`, sans écraser un fichier déjà présent. Ignore les photos sans `premier_niveau`, sans JPEG, ou `agrandi=False` |
| `MigrateOldGpsToLieu` | ne plus lancer | Retourne tout de suite |
| `FillFromLegacyCppDb` | ne plus lancer | Retourne tout de suite |

Il n'y a pas de signaux Django. Les effets de bord sont `PhotoModel.save` (checksum) et ces commandes, appelées explicitement.

## Tests

Stratégie écrite dans `PicturesApp/tests/README.md` : ne pas toucher les vraies photos ni la vraie base ; beaucoup de tests de formulaires ; vues avec mocks ; commandes avec `TemporaryDirectory`. `conftest.py` est un placeholder pytest, **inutilisé**. `base.py` pose `override_settings(IMAGES_PATH=tmp)` (la classe « simple » hérite quand même de `TestCase`, pas de `SimpleTestCase`, malgré son nom).

Le gros du jeu est dans `test_forms.py` et `test_views.py`. `test_commands.py` ne vérifie que l'aide d'`ExtractEXIFInfos`. Pas de `test_models.py` malgré le README des tests. Dernier passage de `manage.py test PicturesApp.tests` : 81 tests, OK (la base de test est créée puis détruite ; la base réelle n'est pas touchée).

```bash
cd /home/mehdi/PycharmProjects/PicturesDjango/PicturesDjango
../.venv/bin/python manage.py test PicturesApp.tests --verbosity=2
```

Le runner Django utilise une base de test, pas `db.sqlite3` de production. `TESTING` est vrai parce que `sys.argv` contient `test`. Ne pas lancer les commandes d'import réelles contre `IMAGES_PATH` pour « vérifier » : elles écrivent des fichiers et la vraie base.

## Sauvegarde

`scripts/backup_db.sh`, depuis n'importe où (il retrouve la racine du dépôt) :

- lit `IMAGES_PATH` dans `PicturesDjango/.env` si non déjà dans l'environnement (sans en afficher les autres clés) ;
- snapshot en ligne via l'API `sqlite3` backup (gunicorn peut tourner), compression `zstd -3` ;
- saute si une archive a moins de 6 jours (`FORCE=1` pour forcer) ;
- garde les 4 plus récentes (`KEEP`, `MIN_AGE_DAYS`) ;
- nom : `picturesdjango-db-<date>.sqlite3.zst` dans `IMAGES_PATH/db-backups/`.

Le script suggère un cron dimanche 03:45. Ce n'est pas installé par le dépôt ; ne pas le supposer actif. Variables d'override documentées en tête du script : `PICTURESDJANGO_ENV`, `PICTURESDJANGO_PYTHON`, `PICTURESDJANGO_IMAGES_PATH`, `PICTURESDJANGO_DB`, `PICTURESDJANGO_BACKUP_DIR`.

## Pièges (lus dans le code, pas supposés)

1. README obsolète sur PostgreSQL et `./start_django.sh`. La base est SQLite à côté des images. Le service est gunicorn systemd.
2. Préfixe `/fr/` obligatoire pour l'usage courant. Pas de lien de changement de langue dans l'UI.
3. Écriture seulement si l'hôte est `127.0.0.1` ou `localhost`. Le nom Tailscale et l'IP Tailscale sont lecture seule. L'admin distant répond 404, pas une page de login.
4. Un worker gunicorn : import, resize et copie smartphone figent le site. Timeout 600 s.
5. `ResizeJpegs` est hors transaction. Un échec ensuite laisse des fichiers sans lignes, ou des lignes annulées avec des fichiers déjà là. Relancer l'import du même sujet échoue (« subject already exists ») s'il reste des lignes ; s'il n'en reste pas, le resize intelligent saute les dérivés à jour.
6. `ExtractEXIFInfos` écrase `date` avec la date EXIF. Il ne remplit `lieu` et les champs techniques que s'ils sont vides, et plafonne Nominatim à 99 appels + 1,1 s de pause. Relancer la commande reprend le géocodage là où le plafond l'avait coupé, parce que `lieu` est encore vide.
7. Les coordonnées ne sont écrites que si `longitude is None`.
8. Le lieu GPS ne va plus dans `sujet_dias`. L'ancienne commande de migration est morte.
9. Le checksum est le MD5 du sujet, recalculé à chaque `save()` sans `update_fields` restrictif. Les URL de série en dépendent.
10. Pas d'unicité SQL sur `sujet`.
11. Cache de recherche 15 minutes, invalidé seulement après un import réussi. Une légende modifiée peut rester invisible à la recherche. Cache HTML navigateur 30 s en plus.
12. Séries à un seul niveau de dossier sous `scans/` : importables, absentes de l'arbre d'accueil.
13. Séries de plus de 1000 JPEG visibles : troncature silencieuse côté UI (warning dans les logs pour la planche et la galerie de série).
14. Les routes `Gallery/.../page/<n>/` et `GalleryBySearch/.../page/<n>/` ne correspondent pas à la signature des vues. Utiliser `?page=`.
15. `collectstatic` + redémarrage obligatoires pour le CSS/JS (manifest WhiteNoise). `compilemessages` + redémarrage pour les traductions. `--reload` ne suffit pas.
16. `copy_images_for_smartphone` ne met pas à jour un fichier déjà copié (pas de comparaison de date).
17. Rate-limit des `big` : un diaporama ou un partage HTTPS qui précharge les originaux peut tomber en 429 (20 images / 5 s).
18. `settings.py` logge sur stdout à l'import (`force=True`), y compris pendant les tests.
19. `PicturesApp/tests/base.py` : `PicturesAppSimpleTestCase` étend `TestCase`, donc utilise quand même la base.
20. Les deux commandes legacy retournent tout de suite ; le code qui suit le `return` ne s'exécute pas. Ne pas le décommenter.
21. Fichiers de travail non suivis à la racine : ne pas les committer avec une modification du site.

## Recherche fuzzy

C'est la recherche de photos du site, pas un module à part. Il n'y a pas de commande de management. Le bot ne lance pas une recherche fuzzy tout seul : il ne la touche que si on lui demande de changer `get_search_queryset` ou les vues qui l'appellent.

Périmètre. Tolérance aux fautes sur les mots de la requête, après une première passe SQL exacte. Deux modes, tous les deux fuzzy par défaut (`apply_fuzzy=True`, seuil 75). L'interface ne propose pas de couper le fuzzy.

- Photos (défaut) : champs `sujet_dias`, `commentaire`, `lieu`, `date`, `sujet`. JPEG visible et `premier_niveau` non vide. Max 1000 photos, triées par score.
- Sujets seulement (case `only_subjects`) : champs `date` et `sujet` seulement. Une série par checksum, max 1000. Le boost `sujet_dias` ne s'applique pas.

Pas de tags. Pas de fuzzy sur les noms de fichiers, l'EXIF technique, ni le GPS. Un mot qui est une année (`isdigit`) n'a pas de fuzzy : il doit être exact. Les mots de moins de 2 caractères sont ignorés. La requête est passée par `unidecode` puis mise en minuscules.

Endpoints, sous le préfixe de langue (`/fr/`) :

- `search/` (`search_form`) : formulaire. POST valide vers `SubjectsBySearch` ou `ContactsSheetBySearch`. Seul POST autorisé depuis un hôte distant.
- `ContactsSheetBySearch/<search_term>/` : planche, `get_search_queryset(search_term)`.
- `GalleryBySearch/<search_term>/` (`photo_galleryBySearch`) : galerie, même appel. La variante `.../page/<n>/` ne correspond pas à la vue ; utiliser `?page=`.
- `SubjectsBySearch/<search_term>/` : séries, `search_fields=('date','sujet')`, `result_mode='subjects'`.

Fichiers. `PicturesApp/views.py` (`get_search_queryset`, `rapidfuzz.fuzz.WRatio`, `search_form`, les trois vues de résultats). `PicturesApp/urls.py`. `PicturesApp/forms.py` (`SearchForm`). Templates `search_form.html`, `contactsSheetBySearch.html`, `galleryBySearch.html`, `subjectsBySearch.html`. Dépendance `rapidfuzz`.

Comportement attendu. Phase 1 : chaque mot en `icontains`, union, max 3000 candidats, pas de fuzzy. Phase 2 : score 100 si le token exact est là, sinon `WRatio` sur les tokens assez longs (`max(3, len(mot)-2)`). Un seul mot sous 75 élimine la photo. Score hybride : +12 par mot exact, +18 si l'exact est dans `sujet_dias` (mode photos), plus moyenne et pire score. En dessous de 12, élimination encore. Cache 15 minutes des `pkey` ou checksums ; une légende modifiée peut rester invisible jusqu'à expiration ou jusqu'au prochain import réussi. Le détail chiffré est aussi dans « Recherche (`get_search_queryset`) ».

Ne pas confondre avec l'en-tête `fuzzy` du fichier `django.po` : c'est gettext, pas la recherche.

## Documents déjà dans le dépôt

- `README.md` — installation, venv, pillow-simd, `.env` (noms de variables seulement), debug toolbar, `makemessages`, Tailscale Serve. À corriger mentalement avec ce fichier pour la base et le lancement.
- `PicturesApp/tests/README.md` — stratégie de tests et règles des champs texte.
- `config/picturesdjango-gunicorn.service` et `scripts/backup_db.sh` — en-têtes de commentaires à jour.

Ne pas créer un second document de mémoire : Grok ne charge qu'`AGENTS.md` à la racine git.
