"""
URLs de l'application Documents
"""
from django.urls import path
from apps.documents import views

app_name = 'documents'

urlpatterns = [
    # Liste des documents
    path('', views.DocumentListView.as_view(), name='list'),
    
    # Détail d'un document
    path('<slug:slug>/', views.DocumentDetailView.as_view(), name='detail'),
    
    # Téléchargement
    path('telecharger/<slug:slug>/', views.telecharger_document, name='telecharger'),
]