from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'authentification'

urlpatterns = [
    path('configurer/', views.configurer, name='configurer'),
    path('inscription-privee/', RedirectView.as_view(pattern_name='membres:adhesion', permanent=False), name='inscription_privee'),
]
