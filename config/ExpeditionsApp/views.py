from django.shortcuts import render
from django.http import HttpResponse
from .models import Expedition
# Create your views here.


def home(request):
    return HttpResponse("Welcome to the Expedition App !")


def afficher(request, name):
    return render(request, "expedition/afficher.html", {'name': name})

def listExpeditions(request):
    expeditions = Expedition.objects.all()
    return render(request, "expedition/liste.html", {'expeditions': expeditions})

def detailExpeditions(request):
    expeditions = Expedition.objects.all()
    return render(request, "expedition/detail.html", {'expeditions': expeditions})