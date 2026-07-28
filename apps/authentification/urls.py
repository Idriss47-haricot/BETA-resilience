from django.urls import path
from . import views

app_name = 'authentification'

urlpatterns = [
    path('configurer/', views.configurer, name='configurer'),
    path('inscription-privee/', views.inscription_privee, name='inscription_privee'),
]
