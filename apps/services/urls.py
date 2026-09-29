"""
URLs de l'application Services
"""
from django.urls import path
from apps.services import views

app_name = 'services'

urlpatterns = [
    # Liste des services
    path('', views.ServiceListView.as_view(), name='list'),
    
    # Détail d'un service
    path('<slug:slug>/', views.ServiceDetailView.as_view(), name='detail'),
]