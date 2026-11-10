from django.urls import path
from .views import (VehiculeListView, VehiculeDetailView, VehiculeCreateView,
                    VehiculeUpdateView, VehiculeDeleteView)

app_name = 'vehicule'
urlpatterns = [
    path('', VehiculeListView.as_view(), name='list'),
    path('ajouter/', VehiculeCreateView.as_view(), name='create'),
    path('<int:pk>/', VehiculeDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', VehiculeUpdateView.as_view(), name='update'),
    path('<int:pk>/supprimer/', VehiculeDeleteView.as_view(), name='delete'),
]
