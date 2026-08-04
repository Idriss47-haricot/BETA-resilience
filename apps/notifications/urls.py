from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.liste, name='liste'),
    path('marquer-toutes-lues/', views.marquer_toutes_lues, name='marquer_toutes_lues'),
    path('preferences/', views.preferences, name='preferences'),
    path('messagerie/', views.messagerie_admin, name='messagerie_admin'),
    path('messagerie/<int:membre_id>/', views.messagerie_admin, name='messagerie_admin_membre'),
    path('mes-messages/', views.messagerie_membre, name='messagerie_membre'),
]
