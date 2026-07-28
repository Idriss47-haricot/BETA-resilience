"""
URLs de l'application Partenaires
"""
from django.urls import path
from apps.partenaires import views

app_name = 'partenaires'

urlpatterns = [
    # Liste des partenaires
    path('', views.PartenaireListView.as_view(), name='list'),
    
    # Détail d'un partenaire
    path('<slug:slug>/', views.PartenaireDetailView.as_view(), name='detail'),
]