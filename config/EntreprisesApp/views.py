from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Entreprise
from .forms import EntrepriseForm


class EntrepriseListView(ListView):
    model = Entreprise
    template_name = 'entreprises/list.html'
    context_object_name = 'entreprises'
    queryset = Entreprise.objects.select_related('gerant').order_by('raison_sociale')


class EntrepriseDetailView(DetailView):
    model = Entreprise
    template_name = 'entreprises/detail.html'
    context_object_name = 'entreprise'


class EntrepriseCreateView(CreateView):
    model = Entreprise
    form_class = EntrepriseForm
    template_name = 'shared/form.html'
    success_url = reverse_lazy('entreprise:list')
    extra_context = {'page_title': 'Ajouter une entreprise', 'list_url_name': 'entreprise:list', 'submit_label': 'Créer l’entreprise'}


class EntrepriseUpdateView(UpdateView):
    model = Entreprise
    form_class = EntrepriseForm
    template_name = 'shared/form.html'
    success_url = reverse_lazy('entreprise:list')
    extra_context = {'page_title': 'Modifier l’entreprise', 'list_url_name': 'entreprise:list', 'submit_label': 'Enregistrer les modifications'}


class EntrepriseDeleteView(DeleteView):
    model = Entreprise
    template_name = 'shared/confirm_delete.html'
    success_url = reverse_lazy('entreprise:list')
    extra_context = {'list_url_name': 'entreprise:list', 'delete_warning': 'Attention : supprimer cette entreprise supprimera aussi son compte gérant, ses expéditions, ses véhicules et les offres associées.'}
