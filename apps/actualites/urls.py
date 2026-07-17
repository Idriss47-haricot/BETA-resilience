"""
URLs de l'application Actualités
"""
from django.urls import path
from apps.actualites import views

app_name = 'actualites'

urlpatterns = [
    # Liste des actualités
    path('', views.ActualiteListView.as_view(), name='list'),
    
    # Détail d'un article
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='detail'),
    
    # Articles par catégorie
    path('categorie/<slug:slug>/', views.CategorieView.as_view(), name='categorie'),
]