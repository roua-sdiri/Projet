from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

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

    capacite_kg = models.PositiveIntegerField(validators=[MinValueValidator(1,"La capacite doit etre superieure a 0 kg.")])

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


def clean(self):
    super().clean()

    if self.entreprise and self.entreprise.type_entreprise != 'transporteur':
        raise ValidationError({
            'entreprise': "L'entreprise du véhicule doit être de type transporteur."
        })


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
