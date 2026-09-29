"""
URLs de l'application Demandes
"""
from django.urls import path
from apps.demandes import views
from django.contrib.auth import views as auth_views


app_name = 'demandes'

urlpatterns = [
    # Formulaire de demande
    path('soumettre/', views.DemandeView.as_view(), name='soumettre'),
    path('succes/', views.DemandeSuccesView.as_view(), name='succes'),
    
    # Admin - Liste et détail
    path('liste/', views.DemandesListView.as_view(), name='liste'),
    path('detail/<int:pk>/', views.DemandeDetailView.as_view(), name='detail'),
    

]