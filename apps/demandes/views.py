"""
Vues de l'application Demandes
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse

from apps.demandes.models import Demande
from apps.demandes.forms import DemandeForm


class AccueilView(TemplateView):
    """
    Page d'accueil avec les entités
    """
    template_name = 'core/accueil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Informations sur les entités
        context['entites'] = [
            {
                'slug': 'association',
                'nom': 'BETA-Résilience Association',
                'description': 'Rejoignez notre réseau associatif et participez à des actions de résilience socio-environnementale.',
                'icone': 'fa-users',
                'couleur': '#2E7D32',
                'badge': 'Association',
                'stats': '30+ membres actifs',
            },
            {
                'slug': 'bureau_etude',
                'nom': 'BETA-Résilience Bureau d\'étude',
                'description': 'Expertise et conseil en environnement, études d\'impact, cartographie et géomatique.',
                'icone': 'fa-building',
                'couleur': '#1565C0',
                'badge': 'Bureau d\'étude',
                'stats': '10+ études réalisées',
            },
            {
                'slug': 'invest',
                'nom': 'BETA-Résilience INVEST',
                'description': 'Investissements durables dans l\'agriculture, l\'immobilier, la pisciculture et l\'agroécologie.',
                'icone': 'fa-chart-line',
                'couleur': '#E65100',
                'badge': 'INVEST',
                'stats': '5+ projets financés',
            },
            {
                'slug': 'laboratoire',
                'nom': 'Laboratoire Résilience',
                'description': 'Recherche scientifique transdisciplinaire sur la résilience des sociétés et des écosystèmes.',
                'icone': 'fa-flask',
                'couleur': '#6A1B9A',
                'badge': 'Laboratoire',
                'stats': '15+ publications scientifiques',
            },
        ]
        
        # Statistiques globales
        context['stats_globales'] = {
            'demandes': Demande.objects.count(),
            'en_attente': Demande.objects.filter(statut='en_attente').count(),
            'traitees': Demande.objects.filter(statut='traite').count(),
        }
        
        return context


class DemandeView(CreateView):
    """
    Formulaire de soumission de demande
    """
    model = Demande
    form_class = DemandeForm
    template_name = 'demandes/demande_form.html'
    success_url = reverse_lazy('demandes:succes')
    
    def form_valid(self, form):
        # Sauvegarder la demande
        self.object = form.save(commit=False)
        self.object.ip_address = self.request.META.get('REMOTE_ADDR', '')
        self.object.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        self.object.save()
        
        # Envoyer email de confirmation à l'utilisateur
        self.envoyer_email_confirmation(self.object)
        
        # Envoyer email de notification à l'administrateur
        self.envoyer_email_notification(self.object)
        
        messages.success(self.request, 'Votre demande a été envoyée avec succès. Nous vous répondrons dans les plus brefs délais.')
        return super().form_valid(form)
    
    def envoyer_email_confirmation(self, demande):
        """
        Envoyer un email de confirmation à l'utilisateur
        """
        try:
            sujet = f'Confirmation de votre demande - {demande.get_entite_display()}'
            
            context = {
                'demande': demande,
                'site_name': settings.SITE_NAME,
            }
            
            message_html = render_to_string('demandes/email_confirmation.html', context)
            
            email = EmailMessage(
                sujet,
                message_html,
                settings.DEFAULT_FROM_EMAIL,
                [demande.email],
                reply_to=[settings.CONTACT_EMAIL],
            )
            email.content_subtype = 'html'
            email.send(fail_silently=True)
        except Exception as e:
            print(f"Erreur d'envoi d'email de confirmation: {e}")
    
    def envoyer_email_notification(self, demande):
        """
        Envoyer un email de notification à l'administrateur
        """
        try:
            sujet = f'[BETA-Résilience] Nouvelle demande - {demande.get_entite_display()}'
            
            context = {
                'demande': demande,
                'site_name': settings.SITE_NAME,
                'admin_url': settings.ADMIN_URL,
            }
            
            message_html = render_to_string('demandes/email_notification.html', context)
            
            email = EmailMessage(
                sujet,
                message_html,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                reply_to=[demande.email],
            )
            email.content_subtype = 'html'
            email.send(fail_silently=True)
        except Exception as e:
            print(f"Erreur d'envoi d'email de notification: {e}")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entite'] = self.request.GET.get('entite', '')
        return context


class DemandeSuccesView(TemplateView):
    """
    Page de confirmation après soumission
    """
    template_name = 'demandes/demande_succes.html'


class DemandeDetailView(DetailView):
    """
    Détail d'une demande (admin)
    """
    model = Demande
    template_name = 'demandes/demande_detail.html'
    context_object_name = 'demande'


class DemandesListView(ListView):
    """
    Liste des demandes (admin)
    """
    model = Demande
    template_name = 'demandes/demandes_list.html'
    context_object_name = 'demandes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        entite = self.request.GET.get('entite')
        statut = self.request.GET.get('statut')
        
        if entite:
            queryset = queryset.filter(entite=entite)
        if statut:
            queryset = queryset.filter(statut=statut)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entites'] = Demande.ENTITE_CHOICES
        context['statuts'] = Demande.STATUT_CHOICES
        return context