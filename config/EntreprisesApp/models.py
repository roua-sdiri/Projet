from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Utilisateur(AbstractUser):
    user_id = models.CharField(max_length=8, primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(max_length=100, choices=[('chargeur', 'Chargeur'), ('transporteur', 'Transporteur'), ('administrateur', 'Administrateur')] , default='chargeur')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)






class Entreprise(models.Model):
    raison_sociale = models.CharField(max_length=200, null=False, blank=False)
    matricule_fiscal = models.CharField(max_length=17, null=False, blank=False, unique=True)
    adresse = models.TextField()
    type_entreprise = models.CharField(max_length=100, choices=[('chargeur', 'Chargeur'), ('transporteur', 'Transporteur')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    gerant = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='entreprise')
