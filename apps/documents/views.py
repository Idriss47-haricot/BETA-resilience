"""
Vues de l'application Documents avec gestion des permissions
"""
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from apps.documents.models import Document, CategorieDocument
import mimetypes
import os
from django.conf import settings


class DocumentListView(ListView):
    """
    Liste des documents téléchargeables avec filtres
    """
    model = Document
    template_name = 'documents/documents.html'
    context_object_name = 'documents'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Document.objects.filter(est_publie=True, est_telechargeable=True)
        
        # Filtrer les documents réservés aux membres
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(accessible_aux_membres_seulement=False)
        
        # Filtre par catégorie
        categorie = self.request.GET.get('categorie')
        if categorie:
            queryset = queryset.filter(categorie__slug=categorie)
        
        # Recherche
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                models.Q(titre__icontains=q) | 
                models.Q(description__icontains=q)
            )
        
        return queryset.order_by('categorie', 'ordre', 'titre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Catégories avec comptage
        categories = CategorieDocument.objects.filter(
            documents__est_publie=True
        ).distinct().order_by('ordre')
        
        # Ajouter le comptage pour chaque catégorie
        for cat in categories:
            cat.doc_count = Document.objects.filter(
                categorie=cat, 
                est_publie=True, 
                est_telechargeable=True
            ).count()
        
        context['categories'] = categories
        context['categorie_actuelle'] = self.request.GET.get('categorie', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['is_authenticated'] = self.request.user.is_authenticated
        return context


class DocumentDetailView(DetailView):
    """
    Détail d'un document avec vérification des permissions
    """
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(est_publie=True, est_telechargeable=True)
        
        # Filtrer les documents réservés aux membres
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(accessible_aux_membres_seulement=False)
        
        return queryset


def telecharger_document(request, slug):
    """
    Télécharger un document avec compteur et protection
    """
    # Récupérer le document
    document = get_object_or_404(Document, slug=slug, est_publie=True, est_telechargeable=True)
    
    # Vérifier si le document est réservé aux membres
    if document.accessible_aux_membres_seulement and not request.user.is_authenticated:
        messages.warning(request, 'Ce document est réservé aux membres. Veuillez vous connecter.')
        return redirect('login')
    
    # Vérifier que le fichier existe
    if not document.fichier or not os.path.exists(document.fichier.path):
        messages.error(request, 'Le fichier demandé n\'est plus disponible.')
        return redirect('documents:list')
    
    # Incrémenter le compteur de téléchargements
    document.incrementer_telechargements()
    
    # Déterminer le type MIME
    mime_type, _ = mimetypes.guess_type(document.fichier.path)
    if not mime_type:
        mime_type = 'application/octet-stream'
    
    # Créer la réponse
    response = FileResponse(
        open(document.fichier.path, 'rb'),
        content_type=mime_type
    )
    
    # Ajouter l'en-tête Content-Disposition pour forcer le téléchargement
    filename = document.get_filename()
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


class DocumentDownloadView(View):
    """
    Vue alternative avec gestion des permissions plus avancée
    """
    
    def get(self, request, slug):
        document = get_object_or_404(Document, slug=slug)
        
        # Vérifier les permissions
        if not document.est_publie:
            raise Http404()
        
        if document.accessible_aux_membres_seulement and not request.user.is_authenticated:
            messages.warning(request, 'Ce document est réservé aux membres. Veuillez vous connecter.')
            return redirect('login')
        
        # Vérifier l'existence du fichier
        if not document.fichier or not os.path.exists(document.fichier.path):
            messages.error(request, 'Le fichier demandé n\'est plus disponible.')
            return redirect('documents:list')
        
        # Incrémenter le compteur
        document.incrementer_telechargements()
        
        # Servir le fichier
        try:
            response = FileResponse(
                open(document.fichier.path, 'rb'),
                content_type=mimetypes.guess_type(document.fichier.path)[0] or 'application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{document.get_filename()}"'
            return response
        except Exception as e:
            messages.error(request, 'Une erreur est survenue lors du téléchargement.')
            return redirect('documents:list')