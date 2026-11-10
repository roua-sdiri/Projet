from django.urls import path
from .views import OffreListView, OffreDetailView, OffreCreateView, OffreUpdateView, OffreDeleteView

app_name = 'offre'
urlpatterns = [
    path('', OffreListView.as_view(), name='list'),
    path('ajouter/', OffreCreateView.as_view(), name='create'),
    path('<int:pk>/', OffreDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', OffreUpdateView.as_view(), name='update'),
    path('<int:pk>/supprimer/', OffreDeleteView.as_view(), name='delete'),
]
