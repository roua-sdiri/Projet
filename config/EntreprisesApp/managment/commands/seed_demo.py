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
# recréer) les objets de démo d'un run à l'autre. Le username est le seul champ
# "humainement stable" qu'on contrôle entièrement : le user_id, lui, est un
# CharField(primary_key=True, editable=False) généré par Utilisateur.save() via
# _generate_user_id() (préfixe "AAuser" où AA = les 2 derniers chiffres de l'année,
# puis un compteur sur 2 chiffres, ex. "26user00"). On ne le fixe donc PAS à la main
# : ce serait contourner la logique du modèle. On s'appuie uniquement sur username
# pour retrouver nos utilisateurs de démo.
USERNAME_CHARGEUR = 'demo_chargeur1'
USERNAME_TRANSPORTEUR_1 = 'demo_transporteur1'
USERNAME_TRANSPORTEUR_2 = 'demo_transporteur2'
USERNAMES_DEMO = [USERNAME_CHARGEUR, USERNAME_TRANSPORTEUR_1, USERNAME_TRANSPORTEUR_2]

# Mot de passe de démo uniquement : jamais destiné à un environnement réel.
MOT_DE_PASSE_DEMO = 'Demo1234!'


class Command(BaseCommand):
    help = (
        "Crée un jeu de données de démonstration : 1 entreprise chargeur, 2 "
        "entreprises transporteur (avec véhicule), 2 expéditions (statuts "
        "'publiee' et 'en_cours') et 2 offres concurrentes sur chacune. "
        "Idempotente : peut être relancée sans erreur."
    )

    def handle(self, *args, **options):
        with transaction.atomic():
            self._supprimer_donnees_precedentes()

            chargeur_entreprise = self._creer_chargeur()
            transporteur1_entreprise, vehicule1 = self._creer_transporteur(
                username=USERNAME_TRANSPORTEUR_1,
                email='demo.transporteur1@gmail.com',
                raison_sociale='Transport Demo Nord',
                # Format exigé par matricule_fiscal_validator (EntreprisesApp/models.py) :
                # 7 chiffres + 1 lettre "clé de contrôle" (n'importe laquelle) + 1 lettre
                # parmi A/B/D/N/P + 1 lettre parmi M/P/C/N/E + 3 chiffres. "2222222AAM002"
                # respecte ce format sans avoir besoin de séparateurs (ils sont optionnels).
                matricule_fiscal='2222222AAM002',
                adresse='45 Route de Bizerte, 2000 Ariana, Tunisie',
                immatriculation='DEMO-TR1',
            )
            transporteur2_entreprise, vehicule2 = self._creer_transporteur(
                username=USERNAME_TRANSPORTEUR_2,
                email='demo.transporteur2@gmail.com',
                raison_sociale='Transport Demo Sud',
                matricule_fiscal='3333333AAM003',
                adresse='78 Route de Gabès, 3000 Sfax, Tunisie',
                immatriculation='DEMO-TR2',
            )

            # --- Expédition 1 : reste 'publiee', offres encore actives -------------
            expedition1 = self._creer_expedition(
                chargeur_entreprise,
                numero=1,
                jours_avant_depart=7,
                ville_depart='Tunis',
                ville_arrivee='Sfax',
                # 1200 kg : dans la plage (0, 1500] kg du gabarit 'camionnette' des 2
                # véhicules de démo (cf. _creer_transporteur), condition nécessaire
                # pour que les offres passent la règle 7 d'Offre.clean().
                poids_kg=Decimal('1200.00'),
                description="Expédition de démonstration (statut 'publiee') créée par seed_demo.",
            )
            self._creer_offres(
                expedition1, transporteur1_entreprise, vehicule1, transporteur2_entreprise, vehicule2,
                prix1=Decimal('800.00'), delai1=3,
                prix2=Decimal('950.50'), delai2=5,
            )

            # --- Expédition 2 : offres créées, PUIS statut passé à 'en_cours' ------
            # Offre.clean() (règle 3) interdit de créer une NOUVELLE offre si
            # l'expédition n'est pas 'publiee' : il faut donc créer les offres
            # d'abord (pendant que le statut par défaut est encore 'publiee'), et ne
            # faire passer l'expédition à 'en_cours' qu'ensuite. Ça donne une 2e
            # expédition dans un statut différent de la 1re, utile pour tester le
            # badge coloré par statut et l'action groupée "Clôturer les expéditions
            # sélectionnées" (qui ne traite que 'en_cours').
            expedition2 = self._creer_expedition(
                chargeur_entreprise,
                numero=2,
                jours_avant_depart=10,
                ville_depart='Sousse',
                ville_arrivee='Gabès',
                poids_kg=Decimal('800.00'),  # toujours dans la plage 'camionnette' (0, 1500] kg.
                description="Expédition de démonstration (statut 'en_cours') créée par seed_demo.",
            )
            self._creer_offres(
                expedition2, transporteur1_entreprise, vehicule1, transporteur2_entreprise, vehicule2,
                prix1=Decimal('600.00'), delai1=2,
                prix2=Decimal('680.00'), delai2=4,
            )
            expedition2.statut = 'en_cours'
            # .save() (et non .update()) pour que full_clean()/clean() s'exécutent
            # bien sur ce changement de statut, comme partout ailleurs dans ce projet.
            expedition2.save()

        self.stdout.write(self.style.SUCCESS(
            "Jeu de données de démonstration créé avec succès. "
            f"Expéditions de référence : {expedition1.reference} (publiee), "
            f"{expedition2.reference} (en_cours)."
        ))

    def _supprimer_donnees_precedentes(self):
        """
        Supprime les Utilisateur de démo d'un run précédent, s'ils existent.
        Le CASCADE des FK/O2O du projet fait le reste (voir docstring du module) :
        pas de risque de doublon ni d'erreur de contrainte d'unicité au prochain
        appel de la commande (matricule_fiscal, immatriculation, reference sont tous
        unique=True).
        """
        nb_supprimes, _ = Utilisateur.objects.filter(username__in=USERNAMES_DEMO).delete()
        if nb_supprimes:
            self.stdout.write(f"Anciennes données de démo supprimées ({nb_supprimes} ligne(s)).")

    def _creer_utilisateur(self, username, email, role):
        """
        Utilisateur.objects.create_user(...) (hérité de Django via AbstractUser,
        aucun manager custom n'est défini sur Utilisateur) est la bonne méthode ici :
        elle hache le mot de passe via set_password() avant l'appel à .save().
        C'est ce .save() surchargé (EntreprisesApp/models.py) qui, lui, génère
        automatiquement user_id puisqu'il est vide à ce stade, puis appelle
        full_clean() - donc l'email doit déjà respecter validate_email (obligatoire,
        se terminer par "@gmail.com") avant même d'arriver ici.
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
            # 20 caractères minimum exigés par MinLengthValidator sur Entreprise.adresse.
            matricule_fiscal='1111111AAM001',
            type_entreprise='chargeur',
            adresse='12 Avenue Habib Bourguiba, 1000 Tunis, Tunisie',
            gerant=utilisateur,
        )

    def _creer_transporteur(self, username, email, raison_sociale, matricule_fiscal, adresse, immatriculation):
        """
        Crée une entreprise transporteur avec son utilisateur-gérant et un véhicule
        disponible. Le véhicule doit être créé APRÈS l'entreprise transporteur : le
        clean() de Vehicule (VehiculesApp/models.py) exige que
        entreprise.type_entreprise == 'transporteur', déjà garanti ici.
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
            # rester compatible avec le poids des 2 expéditions de démo (1200 kg et
            # 800 kg, cf. _creer_expedition), sinon la règle 7 d'Offre.clean()
            # rejetterait les offres.
            type_vehicule='camionnette',
            capacite_kg=1200,
            disponible=True,  # requis par la règle 6 d'Offre.clean() à la création d'une offre.
            entreprise=entreprise,
        )
        return entreprise, vehicule

    def _creer_expedition(self, chargeur_entreprise, numero, jours_avant_depart, ville_depart, ville_arrivee,
                           poids_kg, description):
        """
        numero (1, 2, ...) numérote la référence générée pour cette expédition de
        démo (EXP-{année}-000{numero}) ; voir plus bas pourquoi on la fixe nous-mêmes
        au lieu de laisser Expedition._generate_reference() s'en charger.
        """
        expedition = Expedition(
            # date_souhaitee n'a pas de contrainte "dans le futur" dans le modèle,
            # mais une date à J+N est plus parlante dans une démo qu'une date figée.
            date_souhaitee=timezone.now().date() + timedelta(days=jours_avant_depart),
            ville_depart=ville_depart,
            ville_arrivee=ville_arrivee,
            poids_kg=poids_kg,
            description=description,
            # statut='publiee' (valeur par défaut du champ) est indispensable ici,
            # même pour l'expédition qu'on fera passer à 'en_cours' juste après :
            # Offre.clean() (règle 3) interdit de créer une offre sur une expédition
            # dont le statut n'est pas encore 'publiee'.
            entreprise=chargeur_entreprise,
        )
        # Expedition.save() ne génère automatiquement `reference` que si le champ est
        # vide (`if not self.reference`). On le fixe nous-mêmes ici pour obtenir une
        # référence stable et reconnaissable d'un run à l'autre (ex. "EXP-26-00001"),
        # plutôt que de laisser le compteur automatique dépendre du contenu de la
        # base au moment de l'exécution (ce qui romprait l'idempotence : un autre
        # run, ou d'autres expéditions déjà en base, décaleraient le numéro). On
        # reproduit exactement le format attendu par _generate_reference()
        # (EXP-{2 derniers chiffres de l'année}-{numéro sur 5 chiffres}) plutôt que
        # de coder "26" en dur, pour que ce script reste correct si on le rejoue une
        # autre année.
        annee = timezone.now().strftime('%y')
        expedition.reference = f"EXP-{annee}-{numero:05d}"
        expedition.save()
        return expedition

    def _creer_offres(self, expedition, transporteur1_entreprise, vehicule1, transporteur2_entreprise, vehicule2,
                       prix1, delai1, prix2, delai2):
        # Prix et délais volontairement différents pour illustrer 2 offres
        # concurrentes comparables sur la même expédition (ex. dans l'admin ou une
        # future vue de comparaison d'offres).
        Offre.objects.create(
            transporteur=transporteur1_entreprise,
            expedition=expedition,
            vehicule=vehicule1,
            prix=prix1,
            delai_jours=delai1,
            # statut='proposee' est la valeur par défaut du champ.
        )
        Offre.objects.create(
            transporteur=transporteur2_entreprise,
            expedition=expedition,
            vehicule=vehicule2,
            prix=prix2,
            delai_jours=delai2,
        )
