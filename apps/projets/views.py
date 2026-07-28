"""
Vues de l'application Projets
"""
from django.views.generic import ListView, DetailView
from django.db.models import Q
from apps.projets.models import Projet, CategorieProjet


class ProjetListView(ListView):
    """
    Liste des projets avec filtres
    """
    model = Projet
    template_name = 'projets/projets.html'
    context_object_name = 'projets'
    paginate_by = 9  # 9 projets par page
    
    def get_queryset(self):
        queryset = Projet.objects.filter(est_publie=True).order_by('-date_debut')
        
        # Filtre par statut
        statut = self.request.GET.get('statut')
        if statut == 'en_cours':
            queryset = queryset.filter(statut='en_cours')
        elif statut == 'boucle':
            queryset = queryset.filter(statut='boucle')
        
        # Filtre par catégorie
        categorie = self.request.GET.get('categorie')
        if categorie:
            queryset = queryset.filter(categories__slug=categorie)
        
        # Recherche
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(titre__icontains=q) | 
                Q(description_courte__icontains=q) |
                Q(description_longue__icontains=q)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategorieProjet.objects.all().order_by('ordre')
        context['statut_actuel'] = self.request.GET.get('statut', 'tous')
        context['categorie_actuelle'] = self.request.GET.get('categorie', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ProjetDetailView(DetailView):
    """
    Détail d'un projet
    """
    model = Projet
    template_name = 'projets/projet_detail.html'
    context_object_name = 'projet'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Projets similaires (même catégorie)
        projet = self.get_object()
        context['projets_similaires'] = Projet.objects.filter(
            est_publie=True,
            categories__in=projet.categories.all()
        ).exclude(id=projet.id).distinct()[:3]
        
        # Étapes du projet
        context['etapes'] = projet.etapes.all().order_by('ordre')
        
        return context