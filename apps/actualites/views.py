"""
Vues de l'application Actualités - Version finale
"""
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone

from apps.actualites.models import Article, CategorieActualite, Commentaire
from apps.actualites.forms import CommentaireForm


class ActualiteListView(ListView):
    """
    Liste des actualités avec filtres et recherche
    """
    model = Article
    template_name = 'actualites/actualites.html'
    context_object_name = 'articles'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = Article.objects.filter(
            est_publie=True,
            statut='publie'
        ).order_by('-date_publication')
        
        # Filtrer les articles programmés
        queryset = queryset.filter(date_publication__lte=timezone.now())
        
        # Filtre par catégorie
        categorie = self.request.GET.get('categorie')
        if categorie:
            queryset = queryset.filter(categories__slug=categorie)
        
        # Filtre par type (blog, actualité, événement)
        type_article = self.request.GET.get('type')
        if type_article:
            queryset = queryset.filter(categories__slug=type_article)
        
        # Recherche
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(titre__icontains=q) | 
                Q(contenu__icontains=q) |
                Q(tags__icontains=q) |
                Q(extrait__icontains=q)
            )
        
        # Articles à la une en premier
        queryset = queryset.order_by('-est_a_la_une', '-date_publication')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Catégories avec nombre d'articles
        categories = CategorieActualite.objects.filter(
            est_active=True,
            articles__est_publie=True
        ).distinct().annotate(
            nb_articles=Count('articles')
        ).order_by('ordre')
        
        context['categories'] = categories
        context['categorie_actuelle'] = self.request.GET.get('categorie', '')
        context['type_actuel'] = self.request.GET.get('type', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        # Articles à la une
        context['articles_a_la_une'] = Article.objects.filter(
            est_publie=True,
            est_a_la_une=True,
            date_publication__lte=timezone.now()
        ).order_by('-date_publication')[:3]
        
        return context


class ArticleDetailView(DetailView):
    """
    Détail d'un article avec commentaires et articles similaires
    """
    model = Article
    template_name = 'actualites/article_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Vérifier si l'article est publié
        if not self.object.est_publie:
            messages.warning(request, 'Cet article n\'est pas encore publié.')
            return redirect('actualites:list')
        
        # Incrémenter les vues
        self.object.incrementer_vues()
        
        context = self.get_context_data(object=self.object)
        context['form'] = CommentaireForm()
        
        # Articles similaires (mêmes catégories)
        categories = self.object.categories.all()
        if categories.exists():
            context['articles_similaires'] = Article.objects.filter(
                est_publie=True,
                categories__in=categories
            ).exclude(id=self.object.id).distinct()[:3]
        else:
            context['articles_similaires'] = Article.objects.filter(
                est_publie=True
            ).exclude(id=self.object.id).order_by('-date_publication')[:3]
        
        # Commentaires approuvés
        context['commentaires'] = self.object.commentaires.filter(est_approuve=True)
        
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentaireForm(request.POST)
        
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = self.object
            commentaire.ip_address = request.META.get('REMOTE_ADDR', '')
            commentaire.user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Auto-approbation si pas de modération
            commentaire.save()
            
            # Incrémenter le compteur
            self.object.incrementer_commentaires()
            
            messages.success(request, 'Votre commentaire a été ajouté avec succès.')
            return HttpResponseRedirect(self.object.get_absolute_url())
        
        messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
        
        context = self.get_context_data(object=self.object)
        context['form'] = form
        context['commentaires'] = self.object.commentaires.filter(est_approuve=True)
        
        return self.render_to_response(context)


class CategorieView(ListView):
    """
    Articles par catégorie
    """
    model = Article
    template_name = 'actualites/categorie.html'
    context_object_name = 'articles'
    paginate_by = 6
    
    def get_queryset(self):
        self.categorie = get_object_or_404(CategorieActualite, slug=self.kwargs['slug'])
        return Article.objects.filter(
            est_publie=True,
            categories=self.categorie,
            date_publication__lte=timezone.now()
        ).order_by('-date_publication')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorie'] = self.categorie
        return context


class ArticleArchiveView(TemplateView):
    """
    Archive des articles par date
    """
    template_name = 'actualites/archive.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer l'année et le mois depuis l'URL
        annee = self.kwargs.get('annee')
        mois = self.kwargs.get('mois')
        
        context['annee'] = annee
        context['mois'] = mois
        
        if annee and mois:
            # Articles pour un mois spécifique
            context['articles'] = Article.objects.filter(
                est_publie=True,
                date_publication__year=annee,
                date_publication__month=mois
            ).order_by('-date_publication')
        elif annee:
            # Articles pour une année spécifique
            context['articles'] = Article.objects.filter(
                est_publie=True,
                date_publication__year=annee
            ).order_by('-date_publication')
        
        # Liste des années disponibles
        context['annees_disponibles'] = Article.objects.filter(
            est_publie=True
        ).dates('date_publication', 'year', order='DESC')
        
        return context