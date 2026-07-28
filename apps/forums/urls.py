from django.urls import path
from . import views

app_name = 'forums'

urlpatterns = [
    path('', views.ForumIndexView.as_view(), name='index'),
    path('categorie/<slug:slug>/', views.CategorieDetailView.as_view(), name='categorie'),
    path('creer-sujet/<slug:slug>/', views.creer_sujet, name='creer_sujet'),
    path('sujet/<slug:slug>/', views.SujetDetailView.as_view(), name='sujet_detail'),
    path('repondre/<slug:slug>/', views.repondre_sujet, name='repondre'),
]