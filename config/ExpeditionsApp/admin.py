from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.urls import path
from .integrity import run_integrity_checks

from OffresApp.models import Offre
from .models import Expedition


class EnRetardFilter(admin.SimpleListFilter):
    title = 'en retard'
    parameter_name = 'en_retard'

    def lookups(self, request, model_admin):
        return [('oui', 'Oui'), ('non', 'Non')]

    def queryset(self, request, queryset):
        en_retard = Q(statut='publiee', date_souhaitee__lt=timezone.localdate())
        if self.value() == 'oui':
            return queryset.filter(en_retard)
        if self.value() == 'non':
            return queryset.exclude(en_retard)
        return queryset


class OffreInline(admin.StackedInline):
    model = Offre
    fk_name = 'expedition'
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')

    def has_add_permission(self, request, obj=None):
        return False


@admin.action(description="Clôturer les expéditions sélectionnées")
def cloturer_expeditions(modeladmin, request, queryset):
    traitees = ignorees = erreurs = 0
    for expedition in queryset:
        if expedition.statut != 'en_cours':
            ignorees += 1
            continue
        expedition.statut = 'livree'
        try:
            expedition.full_clean()
            expedition.save()
            traitees += 1
        except ValidationError as e:
            erreurs += 1
            modeladmin.message_user(
                request, f"{expedition.reference} : {'; '.join(e.messages)}", messages.ERROR
            )
    modeladmin.message_user(
        request,
        f"{traitees} expédition(s) clôturée(s), {ignorees} ignorée(s) (statut ≠ en cours), {erreurs} en erreur.",
        messages.SUCCESS if traitees else messages.WARNING,
    )


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "integrity-dashboard/",
                self.admin_site.admin_view(self.integrity_dashboard),
                name="expedition_integrity_dashboard",
            ),
        ]

        return custom_urls + urls

    def integrity_dashboard(self, request):
        checks = run_integrity_checks()

        context = {
            **self.admin_site.each_context(request),
            "title": "Tableau de bord d'integrite",
            "checks": checks,
            "total_checks": len(checks),
            "failed_checks": sum(1 for check in checks if not check["ok"]),
        }

        return TemplateResponse(
            request,
            "admin/expeditions_integrity.html",
            context,
        )
    
    list_display = ('reference', 'entreprise', 'ville_depart', 'ville_arrivee',
                    'statut_colore', 'statut', 'date_souhaitee')
    list_filter = ('statut', 'ville_depart', EnRetardFilter)
    search_fields = ('reference', 'ville_depart', 'ville_arrivee', 'entreprise__raison_sociale')
    list_editable = ('statut',)
    ordering = ('-created_at',)
    date_hierarchy = 'date_souhaitee'
    list_per_page = 25
    autocomplete_fields = ('entreprise',)
    readonly_fields = ('reference', 'statut_colore', 'created_at', 'updated_at')
    inlines = [OffreInline]
    actions = [cloturer_expeditions]
    fieldsets = (
        ("Expédition", {"fields": ("reference", "entreprise", "description")}),
        ("Itinéraire et poids", {"fields": ("ville_depart", "ville_arrivee", "poids_kg", "date_souhaitee")}),
        ("Suivi", {"fields": ("statut", "statut_colore", "created_at", "updated_at"),
                   "classes": ("collapse",)}),
    )
    

    @admin.display(description='Statut (badge)')
    def statut_colore(self, obj):
        couleurs = {
            'publiee': '#F0AD4E', 'attribuee': '#5BC0DE', 'en_cours': '#337AB7',
            'livree': '#5CB85C', 'annulee': '#D9534F',
        }
        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:4px;">{}</span>',
            couleurs.get(obj.statut, '#999'), obj.get_statut_display(),
        )

# admin.site.register(Expedition, ExpeditionAdmin)