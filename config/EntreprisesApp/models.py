from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError

def validate_email(value):
    if not value:
        raise ValidationError("Ladresse email est obligatoire")
    if not value.endswith('@gmail.com'):
        raise ValidationError("Domaine invalid")


# Create your models here.
class Utilisateur(AbstractUser):
    user_id = models.CharField(max_length=8, primary_key=True, editable=False)
    email = models.EmailField(unique=True, validators=[validate_email])
    telephone = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(max_length=100, choices=[('chargeur', 'Chargeur'), ('transporteur', 'Transporteur'), ('administrateur', 'Administrateur')] , default='chargeur')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


matricule_fiscal_validator= RegexValidator(regex=r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]\d{3}$', message="Format non conforme")



class Entreprise(models.Model):
    raison_sociale = models.CharField(max_length=200, null=False, blank=False)
    matricule_fiscal = models.CharField(max_length=17, null=False, blank=False, unique=True, validators=[matricule_fiscal_validator])
    adresse = models.TextField(validators=[MinLengthValidator(20, "Ladresse doit contenir au moins 20 caracteres")])
    type_entreprise = models.CharField(max_length=100, choices=[('chargeur', 'Chargeur'), ('transporteur', 'Transporteur')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    gerant = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='entreprise')
