from django import forms
from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule
from .models import Offre


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['expedition', 'transporteur', 'vehicule', 'prix', 'delai_jours', 'statut']
        widgets = {
            'prix': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'delai_jours': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expedition'].queryset = Expedition.objects.filter(statut='publiee').order_by('-created_at')
        self.fields['transporteur'].queryset = Entreprise.objects.filter(type_entreprise='transporteur').order_by('raison_sociale')
        self.fields['vehicule'].queryset = Vehicule.objects.filter(disponible=True).select_related('entreprise').order_by('immatriculation')
        transporteur_id = self.data.get('transporteur') or getattr(self.instance, 'transporteur_id', None)
        if transporteur_id:
            self.fields['vehicule'].queryset = self.fields['vehicule'].queryset.filter(entreprise_id=transporteur_id)
