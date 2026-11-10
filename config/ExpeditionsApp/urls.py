from django.urls import path

from ExpeditionsApp.views import (
    ExpeditionDeleteView,
    ExpeditionDetailView,
    ExpeditionListView,
    afficher,
    detailExpedition,
    home,
    listExpeditions,
    ExpeditionCreateView,
    ExpeditionUpdateView,
)

app_name = 'expedition'

urlpatterns = [
    path('home/', home, name='home'),
    path('afficher/<str:name>/', afficher, name='afficher'),
    path('list/', listExpeditions, name='list_expeditions'),
    path('<int:id>/', detailExpedition, name='detail'),
    path('<int:pk>/deleteview/', ExpeditionDeleteView.as_view(), name='supprimer_expedition'),
    path('listview/', ExpeditionListView.as_view(), name='list_expeditions_view'),
    path('<int:pk>/detailview/', ExpeditionDetailView.as_view(), name='detail_expedition_view'),
    path('create/', ExpeditionCreateView.as_view(), name='create_expedition'),
    path('<int:pk>/update/', ExpeditionUpdateView.as_view(), name='update_expedition'),

]