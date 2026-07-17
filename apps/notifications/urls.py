from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.liste, name='liste'),
    path('marquer-toutes-lues/', views.marquer_toutes_lues, name='marquer_toutes_lues'),
    path('preferences/', views.preferences, name='preferences'),
]