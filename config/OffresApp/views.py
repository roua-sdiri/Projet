from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Offre
from .forms import OffreForm


class OffreListView(ListView):
    model = Offre
    template_name = 'offres/list.html'
    context_object_name = 'offres'
    queryset = Offre.objects.select_related('expedition', 'transporteur', 'vehicule').order_by('-created_at')


class OffreDetailView(DetailView):
    model = Offre
    template_name = 'offres/detail.html'
    context_object_name = 'offre'


class OffreCreateView(CreateView):
    model = Offre
    form_class = OffreForm
    template_name = 'shared/form.html'
    success_url = reverse_lazy('offre:list')
    extra_context = {'page_title': 'Créer une offre', 'list_url_name': 'offre:list', 'submit_label': 'Créer l’offre'}


class OffreUpdateView(UpdateView):
    model = Offre
    form_class = OffreForm
    template_name = 'shared/form.html'
    success_url = reverse_lazy('offre:list')
    extra_context = {'page_title': 'Modifier l’offre', 'list_url_name': 'offre:list', 'submit_label': 'Enregistrer les modifications'}


class OffreDeleteView(DeleteView):
    model = Offre
    template_name = 'shared/confirm_delete.html'
    success_url = reverse_lazy('offre:list')
    extra_context = {'list_url_name': 'offre:list'}
