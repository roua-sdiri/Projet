from django.contrib import admin
from .models import Vehicule


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible', 'entreprise')
    list_filter = ('type_vehicule', 'disponible', 'entreprise')
    search_fields = ('immatriculation', 'entreprise__raison_sociale')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ("Véhicule", {
            "fields": ("immatriculation", "type_vehicule", "capacite_kg", "disponible"),
        }),
        ("Propriétaire", {
            "fields": ("entreprise",),
        }),
        ("Horodatage", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )