from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# Create your models here.
from django.db import models


class Vehicule(models.Model):
    TYPE_VEHICULE_CHOICES = [
        ('camionnette', 'Camionnette'),
        ('fourgon', 'Fourgon'),
        ('camion_porteur', 'Camion porteur'),
        ('semi_remorque', 'Semi-remorque'),
    ]

    immatriculation = models.CharField(max_length=20, unique=True)
    capacite_kg = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "La capacite doit etre superieure a 0 kg.")]
    )
    type_vehicule = models.CharField(max_length=30, choices=TYPE_VEHICULE_CHOICES)
    disponible = models.BooleanField(default=True)
    entreprise = models.ForeignKey(
        'EntreprisesApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='vehicules'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'transporteur':
            raise ValidationError({
                'entreprise': "L'entreprise du véhicule doit être de type transporteur."
            })

    def __str__(self):
        return self.immatriculation

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
