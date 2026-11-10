from django import forms
from django.forms import widgets
from ExpeditionsApp.models import Expedition
class ExpeditionForm (forms.ModelForm):
    class Meta:
        model = Expedition
        fields = ['ville_depart', 'ville_arrivee', 'poids_kg', 'date_souhaitee', 'description', 'statut','entreprise']
        widgets = {
            'date_souhaitee': forms.DateInput(attrs={'type': 'date'})}