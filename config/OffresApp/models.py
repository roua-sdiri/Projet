from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
from decimal import Decimal


class Offre(models.Model):
    STATUT_CHOICES = [
        ('proposee', 'Proposee'),
        ('acceptee', 'Acceptee'),
        ('refusee', 'Refusee'),
        ('retiree', 'Retiree'),
    ]

    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    delai_jours = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='proposee'
    )

    date_proposition = models.DateField(auto_now_add=True)

    expedition = models.ForeignKey(
        'ExpeditionsApp.Expedition',
        on_delete=models.CASCADE,
        related_name='offres'
    )

    transporteur = models.ForeignKey(
        'EntreprisesApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='offres'
    )

    vehicule = models.ForeignKey(
        'VehiculesApp.Vehicule',
        on_delete=models.CASCADE,
        related_name='offres'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['expedition', 'transporteur'],
                condition=Q(statut='proposee'),
                name='unique_proposed_offer_per_company_expedition'
            )
        ]

    def clean(self):
        super().clean()

        if self.transporteur_id:
            if self.transporteur.type_entreprise != 'transporteur':
                raise ValidationError({
                    'transporteur':
                    "Seule une entreprise de type transporteur peut proposer une offre."
                })

        if self.vehicule_id and self.transporteur_id:
            if self.vehicule.entreprise_id != self.transporteur_id:
                raise ValidationError({
                    'vehicule':
                    "Le vehicule doit appartenir au transporteur de l'offre."
                })

        if self.expedition_id and self.vehicule_id:
            poids = self.expedition.poids_kg
            capacite = self.vehicule.capacite_kg

            if poids > capacite:
                raise ValidationError({
                    'vehicule':
                    "La capacite du vehicule est insuffisante pour cette expedition."
                })

            limites = {
                'camionnette': (Decimal('0'), Decimal('1500')),
                'fourgon': (Decimal('0'), Decimal('3500')),
                'camion_porteur': (Decimal('3500'), Decimal('19000')),
                'semi_remorque': (Decimal('19000'), Decimal('26000')),
            }

            type_vehicule = self.vehicule.type_vehicule
            minimum, maximum = limites[type_vehicule]

            if poids > maximum or (
                type_vehicule in ('camion_porteur', 'semi_remorque')
                and poids < minimum
            ):
                raise ValidationError({
                    'vehicule':
                    "Le type de vehicule n'est pas compatible avec le poids de l'expedition."
                })

        if self.statut == 'proposee':
            if self._state.adding:
                if self.expedition_id and self.expedition.statut != 'publiee':
                    raise ValidationError({
                        'expedition':
                        "Une offre ne peut etre creee que pour une expedition publiee."
                    })

                if self.vehicule_id and not self.vehicule.disponible:
                    raise ValidationError({
                        'vehicule':
                        "Ce vehicule n'est pas disponible."
                    })

            if self.expedition_id and self.transporteur_id:
                autres_offres = Offre.objects.filter(
                    expedition_id=self.expedition_id,
                    transporteur_id=self.transporteur_id,
                    statut='proposee'
                )

                if self.pk:
                    autres_offres = autres_offres.exclude(pk=self.pk)

                if autres_offres.exists():
                    raise ValidationError(
                        "Ce transporteur possede deja une offre proposee active pour cette expedition."
                    )

    def save(self, *args, **kwargs):
        with transaction.atomic():
            ancien_statut = None

            if self.pk:
                ancienne_offre = (
                    Offre.objects.filter(pk=self.pk)
                    .values_list('statut', flat=True)
                    .first()
                )
                ancien_statut = ancienne_offre

            self.full_clean()
            super().save(*args, **kwargs)

            if (
                self.statut == 'acceptee'
                and ancien_statut != 'acceptee'
            ):
                expedition = self.expedition
                expedition.statut = 'attribuee'
                expedition.save()

                Offre.objects.filter(
                    expedition_id=self.expedition_id,
                    statut='proposee'
                ).exclude(pk=self.pk).update(statut='refusee')


