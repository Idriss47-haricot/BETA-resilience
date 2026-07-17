"""
URLs de l'application Core
"""
from django.urls import path
from apps.core import views
from django.contrib.auth import views as auth_views


app_name = 'core'

urlpatterns = [
    # Accueil
    path('', views.AccueilView.as_view(), name='accueil'),
    
    # Pages statiques
    path('a-propos/', views.AProposView.as_view(), name='a_propos'),
    path('a-propos/historique/', views.HistoriqueView.as_view(), name='historique'),
    path('a-propos/vision/', views.VisionView.as_view(), name='vision'),
    path('a-propos/missions/', views.MissionsView.as_view(), name='missions'),
    path('a-propos/structuration/', views.StructurationView.as_view(), name='structuration'),
    path('missions/', views.MissionsView.as_view(), name='missions'),
    
    # 🔐 Connexion / Déconnexion
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    

    # Pages dynamiques
    path('page/<slug:slug>/', views.PageDetailView.as_view(), name='page_detail'),
    
    # Conditions
    path('conditions-utilisation/', views.ConditionsView.as_view(), name='conditions'),
    path('mentions-legales/', views.MentionsLegalesView.as_view(), name='mentions_legales'),
    path('admin/notifier/', views.admin_notifier_membres, name='admin_notifier'),

    
]