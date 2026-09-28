from django.db import models
import uuid

# Create your models here.


class Expedition(models.Model):
    STATUT_CHOICES = [
        ('publiee', 'Publiée'),
        ('attribuee', 'Attribuée'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    reference = models.CharField(max_length=12, unique=True, editable=False)

    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)

    poids_kg = models.DecimalField(max_digits=10, decimal_places=2)

    date_souhaitee = models.DateField()
    description = models.TextField(blank=True)

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='publiee')

    entreprise = models.ForeignKey('EntreprisesApp.Entreprise', on_delete=models.CASCADE, related_name='expeditions' )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    