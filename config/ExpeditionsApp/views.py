from django import forms
from django.db.models import ProtectedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from OffresApp.models import Offre
from django.views.generic import ListView, DetailView, DeleteView , CreateView, UpdateView 
from ExpeditionsApp.forms import ExpeditionForm
from ExpeditionsApp.models import Expedition


def home(request):
    return HttpResponse("Welcome to the Expeditions App!")


def afficher(request, name):
    return render(request, 'expeditions/afficher.html', {'name': name})

#option 1: Using function
def listExpeditions(request):
    expeditions = Expedition.objects.all()
    expeditions = (Expedition.objects
                   .select_related('entreprise')
                   .order_by('-created_at'))
    return render(request, 'expeditions/list.html', {'expeditions': expeditions})
#option 2: Using view
class ExpeditionListView(ListView):
    model = Expedition
    template_name = 'expeditions/list.html'
    context_object_name = 'expeditions'
#option 1 using view 
class ExpeditionDetailView(DetailView):
    model = Expedition
    template_name = 'expeditions/detail.html'
    context_object_name = 'expeditions'
#option 2 using function
def detailExpedition(request, id):
    expedition = get_object_or_404(Expedition.objects.select_related('entreprise'), pk=id)
    offres = (Offre.objects
              .filter(expedition=expedition)
              .select_related('transporteur', 'vehicule')
              .order_by('-date_proposition'))
    return render(request, 'expeditions/detail.html',
                  {'expedition': expedition, 'offres': offres})
class ExpeditionDeleteView(DeleteView):
    model = Expedition
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('expedition:list_expeditions')
class ExpeditionCreateView(CreateView):
    model = Expedition
    template_name = 'expeditions/create.html'
    form_class = ExpeditionForm
    success_url = reverse_lazy('expedition:list_expeditions')
class ExpeditionUpdateView(UpdateView):
    model = Expedition
    template_name = 'expeditions/create.html'
    form_class = ExpeditionForm
    success_url = reverse_lazy('expedition:list_expeditions')