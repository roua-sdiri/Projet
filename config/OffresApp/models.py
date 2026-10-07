from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.


class Offre(models.Model):
    STATUT_CHOICES = [
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('retiree', 'Retirée'),
    ]

    prix = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    delai_jours = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='proposee')

    date_proposition = models.DateField(auto_now_add=True)

    expedition = models.ForeignKey('ExpeditionsApp.Expedition', on_delete=models.CASCADE, related_name='offres')

    transporteur = models.ForeignKey('EntreprisesApp.Entreprise', on_delete=models.CASCADE, related_name='offres')

    vehicule = models.ForeignKey('VehiculesApp.Vehicule', on_delete=models.CASCADE, related_name='offres')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

