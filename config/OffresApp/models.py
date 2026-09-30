from django.db import models

# Create your models here.


class Offre(models.Model):
    STATUT_CHOICES = [
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('retiree', 'Retirée'),
    ]

    prix = models.DecimalField(max_digits=5, decimal_places=3)

    delai_jours = models.PositiveIntegerField()

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='proposee')

    date_proposition = models.DateField(auto_now_add=True)

    expedition = models.ForeignKey(Expedition, on_delete=models.CASCADE, related_name='offres')

    transporteur = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='offres')

    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='offres')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

