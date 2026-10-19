from django.contrib import admin
from django.db.models import Q
from django.utils import timezone
from .models import Expedition


class EnRetardFilter(admin.SimpleListFilter):
    title = 'En retard'
    parameter_name = 'en_retard'

    def lookups(self, request, model_admin):
        return [("oui", "Oui"), ("non", "Non")]

    def queryset(self, request, queryset):
        aujourd_hui = timezone.localdate()
        en_retard = Q(statut='publiee', date_souhaitee__lt=aujourd_hui)
        if self.value() == 'oui':
            return queryset.filter(en_retard)
        if self.value() == 'non':
            return queryset.exclude(en_retard)
        return queryset


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrivee', 'statut')
    list_filter = ('statut', 'ville_depart', 'ville_arrivee', "date_souhaitee", EnRetardFilter)
    readonly_fields = ('reference', 'created_at', 'updated_at')
    search_fields = ('reference', 'ville_depart')
    fieldsets = (
        ("Expeditions", {
            "fields": ("reference", "entreprise", "description"),
        }),
        ("Itineraire et poids", {
            "fields": ("ville_depart", "ville_arrivee", "poids_kg", "date_souhaitee"),
        }),
        ("Statut et horodatage", {
            "fields": ("statut", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
# admin.site.register(Expedition, ExpeditionAdmin)