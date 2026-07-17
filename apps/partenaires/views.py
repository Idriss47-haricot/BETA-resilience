"""
Vues de l'application Partenaires
"""
from django.views.generic import ListView, DetailView
from apps.partenaires.models import Partenaire


class PartenaireListView(ListView):
    """
    Liste des partenaires
    """
    model = Partenaire
    template_name = 'partenaires/partenaires.html'
    context_object_name = 'partenaires'
    
    def get_queryset(self):
        return Partenaire.objects.filter(est_actif=True).order_by('ordre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Regrouper les partenaires par type
        types = dict(Partenaire.TYPE_CHOICES)
        context['partenaires_par_type'] = {}
        for type_key, type_label in types.items():
            context['partenaires_par_type'][type_label] = Partenaire.objects.filter(
                est_actif=True,
                type_partenaire=type_key
            ).order_by('ordre')
        
        return context


class PartenaireDetailView(DetailView):
    """
    Détail d'un partenaire
    """
    model = Partenaire
    template_name = 'partenaires/partenaire_detail.html'
    context_object_name = 'partenaire'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'