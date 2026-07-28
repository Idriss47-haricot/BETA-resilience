"""
Vues de l'application Core - Pages principales
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from apps.core.models import Page, SiteConfiguration
from apps.projets.models import Projet, CategorieProjet
from apps.actualites.models import Article, CategorieActualite
from apps.services.models import Service
from apps.partenaires.models import Partenaire
from apps.notifications.models import Notification
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect



class AccueilView(TemplateView):
    """
    Page d'accueil du site
    """
    template_name = 'core/accueil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Derniers projets (3)
        context['derniers_projets'] = Projet.objects.filter(
            est_publie=True
        ).order_by('-date_debut')[:3]
        
        # Dernières actualités (3)
        context['dernieres_actualites'] = Article.objects.filter(
            est_publie=True
        ).order_by('-date_publication')[:3]
        
        # Services mis en avant
        context['services'] = Service.objects.filter(
            est_actif=True,
            est_mis_en_avant=True
        ).order_by('ordre')[:6]
        
        # Tous les services (pour le slider)
        context['tous_services'] = Service.objects.filter(
            est_actif=True
        ).order_by('ordre')
        
        # Partenaires
        context['partenaires'] = Partenaire.objects.filter(
            est_actif=True
        ).order_by('?')[:8]
        
        # Statistiques
        context['stats'] = {
            'membres': 30,  # Nombre de membres
            'projets': Projet.objects.filter(est_publie=True).count(),
            'articles': Article.objects.filter(est_publie=True).count(),
            'partenaires': Partenaire.objects.filter(est_actif=True).count(),
        }
        
        return context


class MissionsView(TemplateView):
    """
    Page Missions
    """
    template_name = 'core/missions.html'

    
class PageDetailView(DetailView):
    """
    Affichage d'une page statique
    """
    model = Page
    template_name = 'core/page_detail.html'
    context_object_name = 'page'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class AProposView(TemplateView):
    """
    Page À Propos
    """
    template_name = 'core/a_propos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer les membres du bureau
        from apps.membres.models import Membre
        context['bureau_executif'] = Membre.objects.filter(
            est_actif=True,
            est_membre_bureau=True
        ).order_by('fonction__ordre')
        context['autres_membres'] = Membre.objects.filter(
            est_actif=True,
            est_membre_bureau=False
        ).order_by('fonction__ordre')
        return context


class HistoriqueView(TemplateView):
    """Page Historique"""
    template_name = 'core/historique.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Lignes de temps de l'historique
        context['timeline'] = [
            {
                'annee': '2017',
                'titre': 'Création de BETA-Résilience Association',
                'description': 'Création de l\'association à but non lucratif par Dr Eric Voundi et ses camarades.'
            },
            {
                'annee': '2021',
                'titre': 'Évolution vers un Groupe',
                'description': 'Transformation en Groupe avec 6 entités inter-opérationnelles.'
            },
            {
                'annee': '2022',
                'titre': 'Lancement du Laboratoire RÉSILIENCE',
                'description': 'Création du laboratoire scientifique dédié à la recherche sur la résilience.'
            },
            {
                'annee': '2023',
                'titre': 'Développement des structures économiques',
                'description': 'Mise en place de BETA-Résilience INVEST et du Bureau d\'étude.'
            },
        ]
        return context


class VisionView(TemplateView):
    """Page Vision"""
    template_name = 'core/vision.html'


class MissionsView(TemplateView):
    """Page Missions"""
    template_name = 'core/missions.html'


class StructurationView(TemplateView):
    """Page Structuration du Groupe"""
    template_name = 'core/structuration.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Organisation du groupe
        context['organes'] = [
            {
                'nom': 'Assemblée Générale',
                'description': 'Organe suprême du Groupe. Composée de tous les membres actifs.',
                'responsabilites': [
                    'Prendre les décisions stratégiques',
                    'Élire le Comité Exécutif',
                    'Valider les rapports d\'activités',
                ]
            },
            {
                'nom': 'Comité Exécutif',
                'description': 'Organe exécutif élu par l\'Assemblée Générale.',
                'responsabilites': [
                    'Exécuter les décisions de l\'AG',
                    'Préparer le budget',
                    'Coordonner les activités du Groupe',
                ]
            },
            {
                'nom': 'Présidence',
                'description': 'Représente le Groupe dans tous les actes de la vie civile.',
                'responsabilites': [
                    'Coordonner les activités du Groupe',
                    'Présider les sessions de l\'AG',
                    'Ordonner les dépenses',
                ]
            },
            {
                'nom': 'Secrétariat Général',
                'description': 'Mémoire du Groupe, gère les documents administratifs.',
                'responsabilites': [
                    'Conserver les documents administratifs',
                    'Rédiger les procès-verbaux',
                    'Élaborer le rapport annuel',
                ]
            },
            {
                'nom': 'Trésorerie',
                'description': 'Gestion des fonds et des comptes du Groupe.',
                'responsabilites': [
                    'Tenir les comptes',
                    'Cosigner les chèques',
                    'Préparer le budget annuel',
                ]
            },
        ]
        return context


class ConditionsView(TemplateView):
    """Page Conditions Générales d'Utilisation"""
    template_name = 'core/conditions.html'


class MentionsLegalesView(TemplateView):
    """Page Mentions Légales"""
    template_name = 'core/mentions_legales.html'

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def redirect_after_login(request):
    return redirect('membres:dashboard')


@staff_member_required
def admin_notifier_membres(request):
    """Page admin pour notifier tous les membres"""
    if request.method == 'POST':
        titre = request.POST.get('titre')
        message = request.POST.get('message')
        type_notif = request.POST.get('type', 'systeme')
        lien = request.POST.get('lien', '')
        envoyer_email = request.POST.get('envoyer_email', False)
        
        if not titre or not message:
            messages.error(request, 'Titre et message sont requis')
            return render(request, 'core/admin_notifier.html')
        
        membres = Membre.objects.filter(est_actif=True, est_compte_active=True)
        count = 0
        
        for membre in membres:
            if membre.user:
                Notification.objects.create(
                    utilisateur=membre.user,
                    type=type_notif,
                    titre=titre,
                    message=message,
                    lien=lien,
                )
                count += 1
        
        messages.success(request, f'✅ Notification envoyée à {count} membres !')
        return redirect('admin:index')
    
    return render(request, 'core/admin_notifier.html')