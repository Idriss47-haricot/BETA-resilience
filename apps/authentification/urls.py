from django.urls import path
from . import views

app_name = 'authentification'

urlpatterns = [
    path('configurer/', views.configurer, name='configurer'),
]