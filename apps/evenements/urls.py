"""
URLs de l'application Événements
"""
from django.urls import path
from apps.evenements import views

app_name = 'evenements'

urlpatterns = [
    path('',                          views.liste,          name='liste'),
    path('mes-evenements/',           views.mes_evenements, name='mes_evenements'),
    path('<slug:slug>/',              views.detail,         name='detail'),
    path('<slug:slug>/inscrire/',     views.s_inscrire,     name='inscrire'),
    path('<slug:slug>/desinscrire/',  views.se_desinscrire, name='desinscrire'),
    path('annuler/<slug:slug>/', views.annuler_inscription, name='annuler'),
    
]