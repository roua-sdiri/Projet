from django.utils import timezone

from OffresApp.models import Offre
from .models import Expedition


def run_integrity_checks():
    checks = []

    def add_check(name, errors):
        errors = list(errors)
        checks.append({
            "name": name,
            "ok": len(errors) == 0,
            "count": len(errors),
            "errors": errors,
        })

    # 1. Une expedition ayant une offre acceptee doit etre attribuee.
    accepted_offers = Offre.objects.filter(
        statut="acceptee"
    ).select_related("expedition")

    errors = [
        f"Offre #{offre.pk} acceptee, mais expedition "
        f"{offre.expedition.reference} au statut "
        f"{offre.expedition.statut}."
        for offre in accepted_offers
        if offre.expedition.statut != "attribuee"
    ]
    add_check("Offres acceptees et statut des expeditions", errors)

    # 2. Une offre acceptee ne doit pas coexister avec une offre proposee.
    errors = []
    accepted_expedition_ids = Offre.objects.filter(
        statut="acceptee"
    ).values_list("expedition_id", flat=True).distinct()

    for expedition in Expedition.objects.filter(
        id__in=accepted_expedition_ids
    ):
        if Offre.objects.filter(
            expedition=expedition, statut="proposee"
        ).exists():
            errors.append(
                f"Expedition {expedition.reference} : "
                "une offre acceptee coexiste avec une offre proposee."
            )
    add_check("Absence d'offres proposees concurrentes", errors)

    # 3. Le vehicule doit appartenir au transporteur de l'offre.
    errors = []
    offers = Offre.objects.select_related("vehicule", "transporteur")

    for offre in offers:
        if offre.vehicule.entreprise_id != offre.transporteur_id:
            errors.append(
                f"Offre #{offre.pk} : le vehicule "
                f"{offre.vehicule.immatriculation} n'appartient pas "
                "au transporteur selectionne."
            )
    add_check("Propriete du vehicule", errors)

    # 4. La capacite du vehicule doit etre suffisante.
    errors = []
    offers = Offre.objects.select_related("vehicule", "expedition")

    for offre in offers:
        if offre.expedition.poids_kg > offre.vehicule.capacite_kg:
            errors.append(
                f"Offre #{offre.pk} : capacite insuffisante pour "
                f"l'expedition {offre.expedition.reference}."
            )
    add_check("Capacite du vehicule", errors)

    # 5. Le transporteur doit etre une entreprise de type transporteur.
    errors = []
    offers = Offre.objects.select_related("transporteur")

    for offre in offers:
        if offre.transporteur.type_entreprise != "transporteur":
            errors.append(
                f"Offre #{offre.pk} : l'entreprise "
                f"{offre.transporteur_id} n'est pas de type transporteur."
            )
    add_check("Type d'entreprise du transporteur", errors)

    # 6. Signaler les expeditions publiees dont la date est depassee.
    today = timezone.localdate()
    late_expeditions = Expedition.objects.filter(
        statut="publiee",
        date_souhaitee__lt=today,
    )

    errors = [
        f"Expedition {expedition.reference} : date souhaitee depassee."
        for expedition in late_expeditions
    ]
    add_check("Expeditions publiees en retard", errors)

    return checks
