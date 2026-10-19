from django.contrib import admin
from .models import Offre


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ('id', 'expedition', 'transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    list_filter = ('statut', 'transporteur')
    search_fields = ('expedition__reference', 'transporteur__raison_sociale', 'vehicule__immatriculation')
    readonly_fields = ('date_proposition', 'created_at', 'updated_at')
    fieldsets = (
        ("Offre", {
            "fields": ("expedition", "transporteur", "vehicule"),
        }),
        ("Conditions", {
            "fields": ("prix", "delai_jours", "statut"),
        }),
        ("Horodatage", {
            "fields": ("date_proposition", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )