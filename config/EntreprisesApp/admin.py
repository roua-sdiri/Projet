from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Entreprise, Utilisateur


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'gerant', 'adresse')
    list_filter = ('type_entreprise',)
    search_fields = ('raison_sociale', 'matricule_fiscale', 'adresse')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ("Entreprise", {
            "fields": ("raison_sociale", "matricule_fiscal", "type_entreprise", "gerant"),
        }),
        ("Coordonnées", {
            "fields": ("adresse",),
        }),
        ("Horodatage", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'telephone', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'telephone')
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')
    fieldsets = UserAdmin.fieldsets + (
        ("Infos supplémentaires", {
            "fields": ("telephone", "role", "created_at", "updated_at"),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Infos supplémentaires", {
            "fields": ("email", "telephone", "role"),
        }),
    )