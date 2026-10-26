from django.urls import path
from .views import home, afficher, listExpeditions


app_name= 'expedition'

urlpatterns = [
    path('home/', home, name='home'),
    path('afficher/<str:name>/', afficher, name='afficher'),
    path('liste/', listExpeditions, name='list_expedition')
    
]
