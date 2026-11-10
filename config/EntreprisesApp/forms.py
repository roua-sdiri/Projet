from django import forms
from .models import Entreprise


class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['raison_sociale', 'matricule_fiscal', 'adresse', 'type_entreprise', 'gerant']
        widgets = {
            'raison_sociale': forms.TextInput(attrs={'placeholder': 'Ex. Transport Express'}),
            'matricule_fiscal': forms.TextInput(attrs={'placeholder': 'Matricule fiscal'}),
            'adresse': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Adresse complète'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gerant'].queryset = self.fields['gerant'].queryset.order_by('username')
