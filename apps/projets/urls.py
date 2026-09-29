"""
URLs de l'application Projets
"""
from django.urls import path
from apps.projets import views

app_name = 'projets'

urlpatterns = [
    # Liste des projets
    path('', views.ProjetListView.as_view(), name='list'),
    
    # Détail d'un projet
    path('<slug:slug>/', views.ProjetDetailView.as_view(), name='detail'),
]