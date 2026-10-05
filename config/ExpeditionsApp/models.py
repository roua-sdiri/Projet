from django.db import models
import uuid
from django.core.exceptions import ValidationError
from django.utils import timezone


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


    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError({'entreprise': 'Une expedition ne peut etre que une entreprise de type chargeur.'})



    @classmethod
    def _generate_reference(cls):
        annee = timezone.now().strftime('%y')

        dernier = cls.objects.filter(reference_startswith=f"EXP_{annee}_").order_by('-reference').first()

        compteur= int(dernier.reference[-5:]) +1 if dernier else 1 

        if compteur > 99999 :
            raise ValidationError("Limit exceeded")
        return f"EXP_{annee}_{compteur:05d}"



    def save(self, *args, **kwargs):
        if not self.reference :
            self.reference = self._generate_reference()
        self.full_clean()
        super().save(*args, **kwargs)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    