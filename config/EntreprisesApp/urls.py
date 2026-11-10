from django.urls import path
from .views import (EntrepriseListView, EntrepriseDetailView, EntrepriseCreateView,
                    EntrepriseUpdateView, EntrepriseDeleteView)

app_name = 'entreprise'
urlpatterns = [
    path('', EntrepriseListView.as_view(), name='list'),
    path('ajouter/', EntrepriseCreateView.as_view(), name='create'),
    path('<int:pk>/', EntrepriseDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', EntrepriseUpdateView.as_view(), name='update'),
    path('<int:pk>/supprimer/', EntrepriseDeleteView.as_view(), name='delete'),
]
