from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from VehiculesApp.models import Vehicule
from .models import Entreprise, Utilisateur

admin.site.site_header = "TransConnect — Administration"
admin.site.site_title = "TransConnect"
admin.site.index_title = "Espace de pilotage des opérations"


class VehiculeInline(admin.TabularInline):
    model = Vehicule
    extra = 0
    fields = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'gerant', 'adresse')
    list_filter = ('type_entreprise',)
    search_fields = ('raison_sociale', 'matricule_fiscal', 'adresse')
    ordering = ('raison_sociale',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
    inlines = [VehiculeInline]
    fieldsets = (
        ("Entreprise", {"fields": ("raison_social", "matricule_fiscal", "type_entreprise", "gerant")}),
        ("Coordonnées", {"fields": ("adresse",)}),
        ("Horodatage", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'telephone', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'telephone')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    list_per_page = 25
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')
    fieldsets = UserAdmin.fieldsets + (
        ("Infos supplémentaires", {"fields": ("telephone", "role", "created_at", "updated_at")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Infos supplémentaires", {"fields": ("email", "telephone", "role")}),
    )