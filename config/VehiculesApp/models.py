from django.db import models

# Create your models here.
from django.db import models


class Vehicule(models.Model):
    TYPE_VEHICULE_CHOICES = [
        ('camionnette', 'Camionnette'),
        ('fourgon', 'Fourgon'),
        ('camion_porteur', 'Camion_porteur'),
        ('semi_remorque', 'Semi_remorque'),
    ]

    immatriculation = models.CharField(
        max_length=20,
        unique=True
    )

    capacite_kg = models.PositiveIntegerField()

    type_vehicule = models.CharField(
        max_length=30,
        choices=TYPE_VEHICULE_CHOICES
    )

    disponible = models.BooleanField(default=True)

    entreprise = models.ForeignKey(
        'EntreprisesApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='vehicules'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
