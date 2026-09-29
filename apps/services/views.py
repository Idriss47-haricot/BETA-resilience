"""
Vues de l'application Services
"""
from django.views.generic import ListView, DetailView
from apps.services.models import Service


class ServiceListView(ListView):
    """
    Liste des services
    """
    model = Service
    template_name = 'services/services.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        return Service.objects.filter(est_actif=True).order_by('ordre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Services par catégorie (on peut ajouter une catégorie si besoin)
        return context


class ServiceDetailView(DetailView):
    """
    Détail d'un service
    """
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'