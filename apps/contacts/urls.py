"""
URLs de l'application Contacts
"""
from django.urls import path
from apps.contacts import views

app_name = 'contacts'

urlpatterns = [
    # Formulaire de contact
    path('', views.ContactView.as_view(), name='contact'),
    
    # Confirmation
    path('succes/', views.ContactSuccesView.as_view(), name='contact_succes'),
]