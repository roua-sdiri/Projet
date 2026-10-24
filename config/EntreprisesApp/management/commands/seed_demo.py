from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from EntreprisesApp.models import Entreprise, Utilisateur
from ExpeditionsApp.models import Expedition
from OffresApp.models import Offre
from VehiculesApp.models import Vehicule

# Identifiants fixes qui permettent de retrouver (et donc de supprimer avant de
# recrÃ©er) les objets de dÃ©mo d'un run Ã  l'autre. Le username est le seul champ
# "humainement stable" qu'on contrÃ´le entiÃ¨rement : le user_id, lui, est un
# CharField(primary_key=True, editable=False) gÃ©nÃ©rÃ© par Utilisateur.save() via
# _generate_user_id() (prÃ©fixe "AAuser" oÃ¹ AA = les 2 derniers chiffres de l'annÃ©e,
# puis un compteur sur 2 chiffres, ex. "26user00"). On ne le fixe donc PAS Ã  la main
# : ce serait contourner la logique du modÃ¨le. On s'appuie uniquement sur username
# pour retrouver nos utilisateurs de dÃ©mo.
USERNAME_CHARGEUR = 'demo_chargeur1'
USERNAME_TRANSPORTEUR_1 = 'demo_transporteur1'
USERNAME_TRANSPORTEUR_2 = 'demo_transporteur2'
USERNAMES_DEMO = [USERNAME_CHARGEUR, USERNAME_TRANSPORTEUR_1, USERNAME_TRANSPORTEUR_2]

# Mot de passe de dÃ©mo uniquement : jamais destinÃ© Ã  un environnement rÃ©el.
MOT_DE_PASSE_DEMO = 'Demo1234!'


class Command(BaseCommand):
    help = (
        "CrÃ©e un jeu de donnÃ©es de dÃ©monstration : 1 entreprise chargeur, 2 "
        "entreprises transporteur (avec vÃ©hicule), 2 expÃ©ditions (statuts "
        "'publiee' et 'en_cours') et 2 offres concurrentes sur chacune. "
        "Idempotente : peut Ãªtre relancÃ©e sans erreur."
    )

    def handle(self, *args, **options):
        with transaction.atomic():
            self._supprimer_donnees_precedentes()

            chargeur_entreprise = self._creer_chargeur()
            transporteur1_entreprise, vehicule1 = self._creer_transporteur(
                username=USERNAME_TRANSPORTEUR_1,
                email='demo.transporteur1@gmail.com',
                raison_sociale='Transport Demo Nord',
                # Format exigÃ© par matricule_fiscal_validator (EntreprisesApp/models.py) :
                # 7 chiffres + 1 lettre "clÃ© de contrÃ´le" (n'importe laquelle) + 1 lettre
                # parmi A/B/D/N/P + 1 lettre parmi M/P/C/N/E + 3 chiffres. "2222222AAM002"
                # respecte ce format sans avoir besoin de sÃ©parateurs (ils sont optionnels).
                matricule_fiscal='2222222AAM002',
                adresse='45 Route de Bizerte, 2000 Ariana, Tunisie',
                immatriculation='DEMO-TR1',
            )
            transporteur2_entreprise, vehicule2 = self._creer_transporteur(
                username=USERNAME_TRANSPORTEUR_2,
                email='demo.transporteur2@gmail.com',
                raison_sociale='Transport Demo Sud',
                matricule_fiscal='3333333AAM003',
                adresse='78 Route de GabÃ¨s, 3000 Sfax, Tunisie',
                immatriculation='DEMO-TR2',
            )

            # --- ExpÃ©dition 1 : reste 'publiee', offres encore actives -------------
            expedition1 = self._creer_expedition(
                chargeur_entreprise,
                numero=1,
                jours_avant_depart=7,
                ville_depart='Tunis',
                ville_arrivee='Sfax',
                # 1200 kg : dans la plage (0, 1500] kg du gabarit 'camionnette' des 2
                # vÃ©hicules de dÃ©mo (cf. _creer_transporteur), condition nÃ©cessaire
                # pour que les offres passent la rÃ¨gle 7 d'Offre.clean().
                poids_kg=Decimal('1200.00'),
                description="ExpÃ©dition de dÃ©monstration (statut 'publiee') crÃ©Ã©e par seed_demo.",
            )
            self._creer_offres(
                expedition1, transporteur1_entreprise, vehicule1, transporteur2_entreprise, vehicule2,
                prix1=Decimal('800.00'), delai1=3,
                prix2=Decimal('950.50'), delai2=5,
            )

            # --- ExpÃ©dition 2 : offres crÃ©Ã©es, PUIS statut passÃ© Ã  'en_cours' ------
            # Offre.clean() (rÃ¨gle 3) interdit de crÃ©er une NOUVELLE offre si
            # l'expÃ©dition n'est pas 'publiee' : il faut donc crÃ©er les offres
            # d'abord (pendant que le statut par dÃ©faut est encore 'publiee'), et ne
            # faire passer l'expÃ©dition Ã  'en_cours' qu'ensuite. Ã‡a donne une 2e
            # expÃ©dition dans un statut diffÃ©rent de la 1re, utile pour tester le
            # badge colorÃ© par statut et l'action groupÃ©e "ClÃ´turer les expÃ©ditions
            # sÃ©lectionnÃ©es" (qui ne traite que 'en_cours').
            expedition2 = self._creer_expedition(
                chargeur_entreprise,
                numero=2,
                jours_avant_depart=10,
                ville_depart='Sousse',
                ville_arrivee='GabÃ¨s',
                poids_kg=Decimal('800.00'),  # toujours dans la plage 'camionnette' (0, 1500] kg.
                description="ExpÃ©dition de dÃ©monstration (statut 'en_cours') crÃ©Ã©e par seed_demo.",
            )
            self._creer_offres(
                expedition2, transporteur1_entreprise, vehicule1, transporteur2_entreprise, vehicule2,
                prix1=Decimal('600.00'), delai1=2,
                prix2=Decimal('680.00'), delai2=4,
            )
            expedition2.statut = 'en_cours'
            # .save() (et non .update()) pour que full_clean()/clean() s'exÃ©cutent
            # bien sur ce changement de statut, comme partout ailleurs dans ce projet.
            expedition2.save()

        self.stdout.write(self.style.SUCCESS(
            "Jeu de donnÃ©es de dÃ©monstration crÃ©Ã© avec succÃ¨s. "
            f"ExpÃ©ditions de rÃ©fÃ©rence : {expedition1.reference} (publiee), "
            f"{expedition2.reference} (en_cours)."
        ))

    def _supprimer_donnees_precedentes(self):
        """
        Supprime les Utilisateur de dÃ©mo d'un run prÃ©cÃ©dent, s'ils existent.
        Le CASCADE des FK/O2O du projet fait le reste (voir docstring du module) :
        pas de risque de doublon ni d'erreur de contrainte d'unicitÃ© au prochain
        appel de la commande (matricule_fiscal, immatriculation, reference sont tous
        unique=True).
        """
        nb_supprimes, _ = Utilisateur.objects.filter(username__in=USERNAMES_DEMO).delete()
        if nb_supprimes:
            self.stdout.write(f"Anciennes donnÃ©es de dÃ©mo supprimÃ©es ({nb_supprimes} ligne(s)).")

    def _creer_utilisateur(self, username, email, role):
        """
        Utilisateur.objects.create_user(...) (hÃ©ritÃ© de Django via AbstractUser,
        aucun manager custom n'est dÃ©fini sur Utilisateur) est la bonne mÃ©thode ici :
        elle hache le mot de passe via set_password() avant l'appel Ã  .save().
        C'est ce .save() surchargÃ© (EntreprisesApp/models.py) qui, lui, gÃ©nÃ¨re
        automatiquement user_id puisqu'il est vide Ã  ce stade, puis appelle
        full_clean() - donc l'email doit dÃ©jÃ  respecter validate_email (obligatoire,
        se terminer par "@gmail.com") avant mÃªme d'arriver ici.
        """
        return Utilisateur.objects.create_user(
            username=username,
            email=email,
            password=MOT_DE_PASSE_DEMO,
            role=role,
        )

    def _creer_chargeur(self):
        utilisateur = self._creer_utilisateur(USERNAME_CHARGEUR, 'demo.chargeur1@gmail.com', role='chargeur')
        return Entreprise.objects.create(
            raison_sociale='Chargeur Demo SARL',
            # 20 caractÃ¨res minimum exigÃ©s par MinLengthValidator sur Entreprise.adresse.
            matricule_fiscal='1111111AAM001',
            type_entreprise='chargeur',
            adresse='12 Avenue Habib Bourguiba, 1000 Tunis, Tunisie',
            gerant=utilisateur,
        )

    def _creer_transporteur(self, username, email, raison_sociale, matricule_fiscal, adresse, immatriculation):
        """
        CrÃ©e une entreprise transporteur avec son utilisateur-gÃ©rant et un vÃ©hicule
        disponible. Le vÃ©hicule doit Ãªtre crÃ©Ã© APRÃˆS l'entreprise transporteur : le
        clean() de Vehicule (VehiculesApp/models.py) exige que
        entreprise.type_entreprise == 'transporteur', dÃ©jÃ  garanti ici.
        """
        utilisateur = self._creer_utilisateur(username, email, role='transporteur')
        entreprise = Entreprise.objects.create(
            raison_sociale=raison_sociale,
            matricule_fiscal=matricule_fiscal,
            type_entreprise='transporteur',
            adresse=adresse,
            gerant=utilisateur,
        )
        vehicule = Vehicule.objects.create(
            immatriculation=immatriculation,
            # 'camionnette' correspond au gabarit (0, 1500] kg dans
            # PLAGES_POIDS_PAR_TYPE_VEHICULE (OffresApp/models.py) : choisi pour
            # rester compatible avec le poids des 2 expÃ©ditions de dÃ©mo (1200 kg et
            # 800 kg, cf. _creer_expedition), sinon la rÃ¨gle 7 d'Offre.clean()
            # rejetterait les offres.
            type_vehicule='camionnette',
            capacite_kg=1200,
            disponible=True,  # requis par la rÃ¨gle 6 d'Offre.clean() Ã  la crÃ©ation d'une offre.
            entreprise=entreprise,
        )
        return entreprise, vehicule

    def _creer_expedition(self, chargeur_entreprise, numero, jours_avant_depart, ville_depart, ville_arrivee,
                           poids_kg, description):
        """
        numero (1, 2, ...) numÃ©rote la rÃ©fÃ©rence gÃ©nÃ©rÃ©e pour cette expÃ©dition de
        dÃ©mo (EXP-{annÃ©e}-000{numero}) ; voir plus bas pourquoi on la fixe nous-mÃªmes
        au lieu de laisser Expedition._generate_reference() s'en charger.
        """
        expedition = Expedition(
            # date_souhaitee n'a pas de contrainte "dans le futur" dans le modÃ¨le,
            # mais une date Ã  J+N est plus parlante dans une dÃ©mo qu'une date figÃ©e.
            date_souhaitee=timezone.now().date() + timedelta(days=jours_avant_depart),
            ville_depart=ville_depart,
            ville_arrivee=ville_arrivee,
            poids_kg=poids_kg,
            description=description,
            # statut='publiee' (valeur par dÃ©faut du champ) est indispensable ici,
            # mÃªme pour l'expÃ©dition qu'on fera passer Ã  'en_cours' juste aprÃ¨s :
            # Offre.clean() (rÃ¨gle 3) interdit de crÃ©er une offre sur une expÃ©dition
            # dont le statut n'est pas encore 'publiee'.
            entreprise=chargeur_entreprise,
        )
        # Expedition.save() ne gÃ©nÃ¨re automatiquement `reference` que si le champ est
        # vide (`if not self.reference`). On le fixe nous-mÃªmes ici pour obtenir une
        # rÃ©fÃ©rence stable et reconnaissable d'un run Ã  l'autre (ex. "EXP-26-00001"),
        # plutÃ´t que de laisser le compteur automatique dÃ©pendre du contenu de la
        # base au moment de l'exÃ©cution (ce qui romprait l'idempotence : un autre
        # run, ou d'autres expÃ©ditions dÃ©jÃ  en base, dÃ©caleraient le numÃ©ro). On
        # reproduit exactement le format attendu par _generate_reference()
        # (EXP-{2 derniers chiffres de l'annÃ©e}-{numÃ©ro sur 5 chiffres}) plutÃ´t que
        # de coder "26" en dur, pour que ce script reste correct si on le rejoue une
        # autre annÃ©e.
        annee = timezone.now().strftime('%y')
        expedition.reference = f"EXP-{annee}-{numero:05d}"
        expedition.save()
        return expedition

    def _creer_offres(self, expedition, transporteur1_entreprise, vehicule1, transporteur2_entreprise, vehicule2,
                       prix1, delai1, prix2, delai2):
        # Prix et dÃ©lais volontairement diffÃ©rents pour illustrer 2 offres
        # concurrentes comparables sur la mÃªme expÃ©dition (ex. dans l'admin ou une
        # future vue de comparaison d'offres).
        Offre.objects.create(
            transporteur=transporteur1_entreprise,
            expedition=expedition,
            vehicule=vehicule1,
            prix=prix1,
            delai_jours=delai1,
            # statut='proposee' est la valeur par dÃ©faut du champ.
        )
        Offre.objects.create(
            transporteur=transporteur2_entreprise,
            expedition=expedition,
            vehicule=vehicule2,
            prix=prix2,
            delai_jours=delai2,
        )

