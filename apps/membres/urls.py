from django.urls import path
from apps.membres import views

app_name = 'membres'

urlpatterns = [
    # Pages existantes
    path('equipe/', views.EquipeView.as_view(), name='equipe'),
    path('membre/<slug:slug>/', views.MembreDetailView.as_view(), name='detail'),
    path('adherer/', views.AdhesionView.as_view(), name='adhesion'),
    path('adherer/succes/', views.AdhesionSuccesView.as_view(), name='adhesion_succes'),
    path('activer-compte/', views.ActivationView.as_view(), name='activation'),
    path('activation-succes/', views.ActivationSuccessView.as_view(), name='activation_succes'),
    
    # ===== NOUVELLES URLs POUR L'ESPACE MEMBRE =====
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profil/', views.ProfilView.as_view(), name='profil'),
    path('mes-demandes/', views.MesDemandesView.as_view(), name='mes-demandes'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),


]