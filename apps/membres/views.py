"""
Vues de l'application Membres - Version complète avec gestion des adhésions
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    CreateView, DetailView, ListView,
    TemplateView, UpdateView, FormView
)
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.demandes.models import Demande
from apps.membres.models import Membre, Fonction, DemandeAdhesion
from apps.membres.utils import generer_carte_membre_response, envoyer_carte_membre_email
from apps.membres.forms import (
    ProfilMembreForm, MembreRegistrationForm, 
    DemandeAdhesionForm, ActivationForm
)
from apps.evenements.models import InscriptionEvenement
from apps.notifications.models import Notification


@staff_member_required
def admin_dashboard(request):
    can_delete_members = request.user.has_perm('membres.delete_membre')
    can_add_members = request.user.has_perm('membres.add_membre')
    can_change_members = request.user.has_perm('membres.change_membre')

    context = {
        'can_delete_members': can_delete_members,
        'can_add_members': can_add_members,
        'can_change_members': can_change_members,
    }
    return render(request, 'membres/admin_dashboard.html', context)


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    """
    Tableau de bord du membre
    """
    template_name = 'membres/dashboard.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            membre = Membre.objects.get(user=self.request.user)
        except Membre.DoesNotExist:
            membre = Membre.objects.create(
                user=self.request.user,
                nom=self.request.user.last_name or 'Nom',
                prenom=self.request.user.first_name or 'Prénom',
                email=self.request.user.email,
                est_actif=True,
                est_compte_active=True,
            )

        context['membre'] = membre
        context['demandes'] = Demande.objects.filter(email=self.request.user.email).order_by('-date_soumission')

        context['inscriptions'] = InscriptionEvenement.objects.filter(
            utilisateur=self.request.user,
            evenement__statut='a_venir'
        ).select_related('evenement').order_by('evenement__date_debut')

        
        context['notifications'] = Notification.objects.filter(
            utilisateur=self.request.user,
            est_lue=False
        ).order_by('-date_creation')
        context['notifications_non_lues'] = context['notifications'].count()

        return context


@method_decorator(login_required, name='dispatch')
class ProfilView(UpdateView):
    """
    Page de profil du membre avec modification
    """
    model = Membre
    form_class = ProfilMembreForm
    template_name = 'membres/profil.html'
    success_url = reverse_lazy('membres:profil')

    def get_object(self, queryset=None):
        return Membre.objects.filter(user=self.request.user).first()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            messages.info(request, "Aucune fiche membre n'est associée à votre compte. Contactez un administrateur.")
            return redirect('/')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            messages.error(request, "Aucune fiche membre n'est associée à votre compte.")
            return redirect('/')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, '✅ Vos informations ont été mises à jour avec succès !')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '❌ Veuillez corriger les erreurs ci-dessous.')
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
class MesDemandesView(ListView):
    """
    Liste des demandes du membre
    """
    template_name = 'membres/mes-demandes.html'
    context_object_name = 'demandes'
    
    def get_queryset(self):
        return Demande.objects.filter(email=self.request.user.email).order_by('-date_soumission')


class ActivationView(FormView):
    """
    Page d'activation de compte
    """
    template_name = 'membres/activation.html'
    form_class = ActivationForm
    success_url = reverse_lazy('login')
    
    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        if not token:
            messages.error(request, '❌ Token d\'activation manquant.')
            return redirect('core:accueil')
        
        try:
            membre = Membre.objects.get(token_activation=token)
            if not membre.verifier_token_activation(token):
                if membre.est_compte_active:
                    messages.warning(request, '⚠️ Votre compte est déjà activé. Veuillez vous connecter.')
                    return redirect('login')
                if membre.est_token_expire():
                    messages.error(request, '⏰ Le lien d\'activation a expiré. Veuillez contacter l\'administrateur.')
                    return redirect('core:accueil')
        except Membre.DoesNotExist:
            messages.error(request, '❌ Token invalide.')
            return redirect('core:accueil')
        
        request.session['activation_token'] = token
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.request.session.get('activation_token')
        try:
            membre = Membre.objects.get(token_activation=token)
            context['membre'] = membre
            context['form'].initial = {
                'email': membre.email,
                'first_name': membre.prenom,
                'last_name': membre.nom,
            }
        except Membre.DoesNotExist:
            pass
        return context
    
    def form_valid(self, form):
        token = self.request.session.get('activation_token')
        try:
            membre = Membre.objects.get(token_activation=token)
            
            if not membre.verifier_token_activation(token):
                messages.error(self.request, '⏰ Le lien d\'activation a expiré.')
                return redirect('core:accueil')
            
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Ce nom d\'utilisateur est déjà pris.')
                return self.form_invalid(form)
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                is_active=True,
            )
            
            membre.activer_compte(user)
            
            if 'activation_token' in self.request.session:
                del self.request.session['activation_token']
            
            messages.success(
                self.request, 
                '✅ Votre compte a été activé avec succès ! Vous pouvez maintenant vous connecter.'
            )
            return super().form_valid(form)
            
        except Membre.DoesNotExist:
            messages.error(self.request, '❌ Token invalide.')
            return redirect('core:accueil')
        except Exception as e:
            messages.error(self.request, f'⚠️ Erreur lors de l\'activation : {str(e)}')
            return self.form_invalid(form)


class ActivationSuccessView(TemplateView):
    """
    Page de confirmation d'activation
    """
    template_name = 'membres/activation_succes.html'


class EquipeView(ListView):
    """
    Page de l'équipe - Liste des membres
    """
    model = Membre
    template_name = 'membres/equipe.html'
    context_object_name = 'membres'
    
    def get_queryset(self):
        return Membre.objects.filter(est_actif=True).order_by(
            '-est_membre_bureau', 'fonction__ordre', 'nom'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bureau_executif'] = self.get_queryset().filter(est_membre_bureau=True)
        context['autres_membres'] = self.get_queryset().filter(est_membre_bureau=False)
        context['fonctions'] = Fonction.objects.filter(est_actif=True).order_by('ordre')
        return context


class MembreDetailView(DetailView):
    """
    Détail d'un membre
    """
    model = Membre
    template_name = 'membres/membre_detail.html'
    context_object_name = 'membre'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class AdhesionView(CreateView):
    """
    Formulaire d'adhésion avec envoi d'email
    """
    model = DemandeAdhesion
    form_class = DemandeAdhesionForm
    template_name = 'membres/adhesion.html'
    success_url = reverse_lazy('membres:adhesion_succes')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Email au demandeur
        try:
            sujet = f"Confirmation de votre demande d'adhésion - {getattr(settings, 'SITE_NAME', 'BETA-Résilience')}"
            message_html = render_to_string('membres/email_confirmation_adhesion.html', {
                'demande': form.instance,
                'site_name': getattr(settings, 'SITE_NAME', 'BETA-Résilience'),
            })
            
            email = EmailMessage(
                sujet,
                message_html,
                settings.DEFAULT_FROM_EMAIL,
                [form.instance.email],
                reply_to=[getattr(settings, 'CONTACT_EMAIL', settings.DEFAULT_FROM_EMAIL)],
            )
            email.content_subtype = 'html'
            email.send(fail_silently=True)
        except Exception as e:
            print(f"Erreur d'envoi d'email: {e}")
        
        # Email aux admins
        try:
            sujet_admin = f"Nouvelle demande d'adhésion - {form.instance.prenom} {form.instance.nom}"
            message_admin = render_to_string('membres/email_notification_admin.html', {
                'demande': form.instance,
                'site_name': getattr(settings, 'SITE_NAME', 'BETA-Résilience'),
                'admin_url': getattr(settings, 'ADMIN_URL', '/admin/'),
            })
            
            email_admin = EmailMessage(
                sujet_admin,
                message_admin,
                settings.DEFAULT_FROM_EMAIL,
                [getattr(settings, 'CONTACT_EMAIL', settings.DEFAULT_FROM_EMAIL)],
            )
            email_admin.content_subtype = 'html'
            email_admin.send(fail_silently=True)
        except Exception as e:
            print(f"Erreur d'envoi d'email admin: {e}")
        
        messages.success(
            self.request, 
            "Votre demande d'adhésion a été envoyée avec succès. Vous recevrez une confirmation par email dans les plus brefs délais."
        )
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Veuillez corriger les erreurs ci-dessous.')
        return super().form_invalid(form)


class AdhesionSuccesView(TemplateView):
    """Page de confirmation d'adhésion"""
    template_name = 'membres/adhesion_succes.html'


@login_required
def telecharger_carte_membre(request, slug):
    """
    Télécharger la carte de membre en PDF
    """
    membre = get_object_or_404(Membre, slug=slug)
    
    if request.user.id != membre.user_id and not request.user.is_superuser:
        messages.error(request, "Vous n'êtes pas autorisé à télécharger cette carte.")
        return redirect('membres:detail', slug=membre.slug)
    
    return generer_carte_membre_response(membre)


@login_required
def envoyer_carte_membre(request, slug):
    """
    Envoyer la carte de membre par email
    """
    membre = get_object_or_404(Membre, slug=slug)
    
    if request.user.id != membre.user_id and not request.user.is_superuser:
        messages.error(request, "Vous n'êtes pas autorisé à envoyer cette carte.")
        return redirect('membres:detail', slug=membre.slug)
    
    try:
        envoyer_carte_membre_email(membre)
        messages.success(request, f'La carte de membre a été envoyée à {membre.email}.')
    except Exception as e:
        messages.error(request, "Une erreur est survenue lors de l'envoi de la carte.")
    
    return redirect('membres:detail', slug=membre.slug)


class MembreInscriptionView(CreateView):
    """
    Inscription d'un nouveau membre (espace membre)
    """
    form_class = MembreRegistrationForm
    template_name = 'membres/inscription.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.'
        )
        return response


class MembreLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return '/admin/'
        return '/membres/dashboard/'
    
    def get_redirect_url(self):
        return None


class MaDemandeDetailView(LoginRequiredMixin, DetailView):
    model = Demande
    template_name = 'membres/ma_demande_detail.html'
    context_object_name = 'demande'
    login_url = '/login/'

    def get_queryset(self):
        return Demande.objects.filter(email=self.request.user.email)
