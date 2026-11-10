from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Vehicule
from .forms import VehiculeForm


class VehiculeListView(ListView):
    model = Vehicule
    template_name = 'vehicules/list.html'
    context_object_name = 'vehicules'
    queryset = Vehicule.objects.select_related('entreprise').order_by('-created_at')


class VehiculeDetailView(DetailView):
    model = Vehicule
    template_name = 'vehicules/detail.html'
    context_object_name = 'vehicule'


class VehiculeCreateView(CreateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'shared/form.html'
    success_url = reverse_lazy('vehicule:list')
    extra_context = {'page_title': 'Ajouter un véhicule', 'list_url_name': 'vehicule:list', 'submit_label': 'Créer le véhicule'}


class VehiculeUpdateView(UpdateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'shared/form.html'
    success_url = reverse_lazy('vehicule:list')
    extra_context = {'page_title': 'Modifier le véhicule', 'list_url_name': 'vehicule:list', 'submit_label': 'Enregistrer les modifications'}


class VehiculeDeleteView(DeleteView):
    model = Vehicule
    template_name = 'shared/confirm_delete.html'
    success_url = reverse_lazy('vehicule:list')
    extra_context = {'list_url_name': 'vehicule:list', 'delete_warning': 'Attention : les offres associées à ce véhicule seront également supprimées.'}
