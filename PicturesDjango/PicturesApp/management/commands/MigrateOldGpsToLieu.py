import re
from django.core.management.base import BaseCommand
from PicturesApp.PhotoModel import PhotoModel
from django.db.models import Q


def looks_like_old_gps_location(text, max_words=5):
    """
    Détecte les anciens libellés GPS.
    - Accepte les formats : "Lieu (Pays)", "Lieu - Lieu (multilingue)", "Lieu, Région, Pays"
    - Tolérance plus intelligente sur les noms belges longs
    - Accepte aussi les noms de pays seuls ("France")
    """
    if not text:
        return False

    text = text.strip()

    # Normalisation des séparateurs
    cleaned = re.sub(r'[-/,()]', ' ', text)
    words = [w.strip() for w in cleaned.split() if w.strip()]

    # Tolérance
    is_belgian = 'belg' in text.lower() or 'belgië' in text.lower()
    if is_belgian:
        effective_max = max(max_words, 8)      # tolérance forte pour les noms belges
    elif ',' in text and text.count(',') >= 2:
        effective_max = max(max_words, 6)      # tolérance légère pour le format "Lieu, Région, Pays"
    else:
        effective_max = max_words

    if len(words) > effective_max:
        return False

    # Détection des motifs classiques
    has_parentheses = bool(re.search(r'\([^)]+\)\s*$', text))
    has_comma_structure = text.count(',') >= 2
    is_just_country = text.lower() in {
        'france', 'belgique', 'belgië', 'espagne', 'allemagne', 'danemark', 'suède'
    }

    if not (has_parentheses or has_comma_structure or is_just_country):
        return False

    # Vérification pays/région
    last_part = text.lower()
    known = {
        'belgique', 'belgië', 'belgien', 'belgium',
        'france',
        'espagne', 'spain', 'españa',
        'allemagne', 'germany', 'deutschland',
        'danemark', 'denmark', 'danmark',
        'suède', 'sweden', 'sverige',
        'bruxelles-capitale', 'bruxelles',
        'pas-de-calais', 'savoie', 'bouches-du-rhône',
        'charleroi', 'dinant', 'ostende', 'hal-vilvorde',
        'sint-gillis', 'woluwe', 'ixelles', 'forest',
        'sint-pieters-leeuw', 'corroy-le-grand',
    }

    for k in known:
        if k in last_part:
            return True

    return False

class Command(BaseCommand):
    help = (
        "Migre les anciennes localisations GPS stockées dans 'sujet_dias' vers le champ 'lieu'.\n"
        "Puis vide le champ 'sujet_dias'.\n\n"
        "Conditions pour migrer une photo :\n"
        "  - Doit avoir des coordonnées GPS (latitude/longitude)\n"
        "  - Le champ 'lieu' doit être vide\n"
        "  - 'sujet_dias' doit ressembler à un ancien libellé GPS : 'Lieu (Pays)'\n"
        "  - Maximum X mots dans sujet_dias (défaut 5)\n\n"
        "Par défaut : mode --dry-run (aucune modification en base)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--execute',
            action='store_true',
            help="Exécute vraiment les modifications (sinon dry-run par défaut)."
        )
        parser.add_argument(
            '--subject-md5',
            type=str,
            default=None,
            help="Limite le traitement à une seule série (checksum)."
        )
        parser.add_argument(
            '--max-words',
            type=int,
            default=5,
            help="Nombre maximum de mots autorisé dans sujet_dias pour considérer que c'est une localisation GPS (défaut: 5)."
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Force le mode simulation (équivalent à ne pas mettre --execute)."
        )

    def handle(self, *args, **options):
        execute = options['execute'] and not options['dry_run']
        subject_md5 = options['subject_md5']
        max_words = options['max_words']

        mode = "EXÉCUTION" if execute else "DRY-RUN (aucune modification)"
        self.stdout.write(self.style.WARNING(f"Mode : {mode}"))
        self.stdout.write(f"Max mots autorisés : {max_words}")

        # Construction du queryset
        qs = PhotoModel.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            lieu__isnull=True,           # on ne touche pas si lieu est déjà rempli
            sujet_dias__isnull=False
        ).exclude(sujet_dias__exact='')

        if subject_md5:
            qs = qs.filter(checksum=subject_md5)
            self.stdout.write(f"Filtre sur la série : {subject_md5}")

        total = qs.count()
        self.stdout.write(f"Photos candidates (GPS + lieu vide + sujet_dias non vide) : {total}")

        if total == 0:
            self.stdout.write(self.style.SUCCESS("Rien à faire."))
            return

        moved = 0
        skipped = 0
        unrecognized = {}   # dict {sujet_dias: count} pour les cas GPS mais non reconnus

        examples_shown = 0
        max_examples = 30

        for photo in qs.iterator():
            sujet_dias = (photo.sujet_dias or "").strip()

            if not looks_like_old_gps_location(sujet_dias, max_words=max_words):
                skipped += 1
                # On enregistre le sujet_dias pour pouvoir l'afficher de façon dédoublonnée
                if sujet_dias not in unrecognized:
                    unrecognized[sujet_dias] = 0
                unrecognized[sujet_dias] += 1
                continue

            # C'est probablement une ancienne localisation GPS
            if execute:
                photo.lieu = sujet_dias
                photo.sujet_dias = ""
                photo.save(update_fields=['lieu', 'sujet_dias'])
                moved += 1
            else:
                moved += 1
                if examples_shown < max_examples:
                    self.stdout.write(
                        f"  [DRY]  pkey={photo.pkey:6d} | {photo.sujet[:35]:<35} | "
                        f"'{sujet_dias}'  →  lieu"
                    )
                    examples_shown += 1
                elif examples_shown == max_examples:
                    self.stdout.write("  [DRY]  ... (autres cas similaires non affichés)")
                    examples_shown += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Terminé.  Déplacements effectués (ou simulés) : {moved}   |   Ignorés par l'heuristique : {skipped}"
        ))

        # Affichage des cas non reconnus en dry-run, dédoublonnés
        if not execute and unrecognized:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING(
                f"⚠️  {len(unrecognized)} valeurs distinctes de 'sujet_dias' ont des coordonnées GPS "
                f"mais n'ont PAS été reconnues comme d'anciennes localisations GPS :"
            ))

            # Trie par nombre d'occurrences décroissant
            sorted_unrecognized = sorted(unrecognized.items(), key=lambda x: x[1], reverse=True)

            for sujet_dias, count in sorted_unrecognized[:80]:   # limite raisonnable
                self.stdout.write(f"     [{count:3d}×]  {sujet_dias}")

            if len(sorted_unrecognized) > 80:
                self.stdout.write(f"     ... et {len(sorted_unrecognized) - 80} autres valeurs distinctes.")

        if not execute:
            self.stdout.write(self.style.WARNING(
                "\nCeci était un DRY-RUN. Aucune modification n'a été faite en base.\n"
                "Relance la commande avec --execute quand tu es prêt (après backup !)."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "\nModifications appliquées. Pense à vérifier quelques photos manuellement."
            ))
