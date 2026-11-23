from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import Profile

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email')
    role = forms.ChoiceField(label='Rôle', choices=Profile.Role.choices)
    telephone = forms.CharField(
    label='Téléphone',
    max_length=15,
    required=False,
    validators=[RegexValidator(r'^\d{8,15}$', 'Le téléphone doit contenir uniquement des chiffres (8 à 15).')],
    widget=forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'placeholder': 'Ex : 98123456'}),
)

    field_order = ['username', 'first_name', 'last_name', 'email', 'role', 'telephone', 'password1', 'password2']

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Cet email est déjà utilisé.')
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.update_or_create(
                user=user,
                defaults={'role': self.cleaned_data['role'], 'telephone': self.cleaned_data['telephone']},
            )
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        labels = {'first_name': 'Prénom', 'last_name': 'Nom', 'email': 'Email'}

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Cet email est déjà utilisé.')
        return email


class ProfileUpdateForm(forms.ModelForm):
    telephone = forms.CharField(
    label='Téléphone',
    max_length=15,
    required=False,
    validators=[RegexValidator(r'^\d{8,15}$', 'Le téléphone doit contenir uniquement des chiffres (8 à 15).')],
    widget=forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'placeholder': 'Ex : 98123456'}),
)