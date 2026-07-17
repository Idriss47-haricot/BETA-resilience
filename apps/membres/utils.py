"""
Utilitaires pour l'envoi d'emails aux membres avec historique
"""
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from apps.membres.models import HistoriqueEmail
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
import string



def enregistrer_historique_email(membre, demande, type_email, sujet, destinataire, contenu, token=None, statut='envoye', message_erreur='', admin_nom='', ip_admin=''):
    """
    Enregistrer un email dans l'historique
    """
    try:
        historique = HistoriqueEmail.objects.create(
            membre=membre,
            demande=demande,
            type_email=type_email,
            sujet=sujet,
            destinataire=destinataire,
            contenu=contenu,
            token=token,
            statut=statut,
            message_erreur=message_erreur,
            admin_nom=admin_nom,
            ip_admin=ip_admin,
        )
        return historique
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de l'historique: {e}")
        return None


def envoyer_invitation(demande, request=None):
    """
    Envoyer l'email d'invitation avec lien d'activation
    """
    try:
        membre = demande.membre
        if not membre:
            raise ValueError("Aucun membre associé à cette demande")
        
        if not membre.token_activation:
            membre.generer_token_activation()
        
        lien_activation = f"{settings.SITE_URL}/activer-compte/?token={membre.token_activation}"
        
        context = {
            'demande': demande,
            'membre': membre,
            'lien_activation': lien_activation,
            'site_name': 'BETA-Résilience',
            'site_url': settings.SITE_URL,
            'expiration_heures': 48,
        }
        
        sujet = '🎉 Félicitations ! Votre adhésion à BETA-Résilience est acceptée'
        message_html = render_to_string('membres/email_invitation.html', context)
        
        admin_nom = request.user.get_full_name() if request and request.user.is_authenticated else ''
        ip_admin = request.META.get('REMOTE_ADDR', '') if request else ''
        
        email = EmailMessage(
            sujet,
            message_html,
            settings.DEFAULT_FROM_EMAIL or 'contact@beta-resilience.org',
            [demande.email],
            reply_to=[settings.CONTACT_EMAIL or 'contact@beta-resilience.org'],
        )
        email.content_subtype = 'html'
        
        try:
            email.send(fail_silently=False)
            statut = 'envoye'
            message_erreur = ''
        except Exception as e:
            statut = 'erreur'
            message_erreur = str(e)
        
        enregistrer_historique_email(
            membre=membre,
            demande=demande,
            type_email='invitation',
            sujet=sujet,
            destinataire=demande.email,
            contenu=message_html,
            token=membre.token_activation,
            statut=statut,
            message_erreur=message_erreur,
            admin_nom=admin_nom,
            ip_admin=ip_admin,
        )
        
        if statut == 'envoye':
            demande.statut = 'invitation_envoyee'
            demande.save()
            if request:
                messages.success(request, f'📧 Invitation envoyée à {demande.email}')
        else:
            if request:
                messages.error(request, f'⚠️ Erreur lors de l\'envoi de l\'invitation: {message_erreur}')
        
        return statut == 'envoye'
        
    except Exception as e:
        if request:
            messages.error(request, f'⚠️ Erreur: {str(e)}')
        return False


def envoyer_refus(demande, request=None):
    """
    Envoyer l'email de refus
    """
    try:
        membre = demande.membre
        
        context = {
            'demande': demande,
            'site_name': 'BETA-Résilience',
            'site_url': settings.SITE_URL,
        }
        
        sujet = '📩 Suite de votre demande d\'adhésion à BETA-Résilience'
        message_html = render_to_string('membres/email_refus.html', context)
        
        admin_nom = request.user.get_full_name() if request and request.user.is_authenticated else ''
        ip_admin = request.META.get('REMOTE_ADDR', '') if request else ''
        
        email = EmailMessage(
            sujet,
            message_html,
            settings.DEFAULT_FROM_EMAIL or 'contact@beta-resilience.org',
            [demande.email],
            reply_to=[settings.CONTACT_EMAIL or 'contact@beta-resilience.org'],
        )
        email.content_subtype = 'html'
        
        try:
            email.send(fail_silently=False)
            statut = 'envoye'
            message_erreur = ''
        except Exception as e:
            statut = 'erreur'
            message_erreur = str(e)
        
        if membre:
            enregistrer_historique_email(
                membre=membre,
                demande=demande,
                type_email='refus',
                sujet=sujet,
                destinataire=demande.email,
                contenu=message_html,
                statut=statut,
                message_erreur=message_erreur,
                admin_nom=admin_nom,
                ip_admin=ip_admin,
            )
        
        if statut == 'envoye':
            if request:
                messages.success(request, f'📧 Email de refus envoyé à {demande.email}')
        else:
            if request:
                messages.error(request, f'⚠️ Erreur lors de l\'envoi du refus: {message_erreur}')
        
        return statut == 'envoye'
        
    except Exception as e:
        if request:
            messages.error(request, f'⚠️ Erreur: {str(e)}')
        return False


def envoyer_rappel_activation(membre, request=None):
    """Envoyer un rappel d'activation 24h avant expiration"""
    try:
        if not membre.token_activation:
            return False
        
        demande = membre.demande_adhesion if hasattr(membre, 'demande_adhesion') else None
        
        lien_activation = f"{settings.SITE_URL}/activer-compte/?token={membre.token_activation}"
        
        context = {
            'membre': membre,
            'lien_activation': lien_activation,
            'site_name': 'BETA-Résilience',
            'site_url': settings.SITE_URL,
        }
        
        sujet = '⏰ Rappel : Activez votre compte BETA-Résilience'
        message_html = render_to_string('membres/email_rappel.html', context)
        
        admin_nom = request.user.get_full_name() if request and request.user.is_authenticated else ''
        ip_admin = request.META.get('REMOTE_ADDR', '') if request else ''
        
        email = EmailMessage(
            sujet,
            message_html,
            settings.DEFAULT_FROM_EMAIL or 'contact@beta-resilience.org',
            [membre.email],
            reply_to=[settings.CONTACT_EMAIL or 'contact@beta-resilience.org'],
        )
        email.content_subtype = 'html'
        
        try:
            email.send(fail_silently=False)
            statut = 'envoye'
            message_erreur = ''
        except Exception as e:
            statut = 'erreur'
            message_erreur = str(e)
        
        enregistrer_historique_email(
            membre=membre,
            demande=demande,
            type_email='rappel',
            sujet=sujet,
            destinataire=membre.email,
            contenu=message_html,
            token=membre.token_activation,
            statut=statut,
            message_erreur=message_erreur,
            admin_nom=admin_nom,
            ip_admin=ip_admin,
        )
        
        return statut == 'envoye'
        
    except Exception as e:
        return False


def envoyer_confirmation_activation(membre, request=None):
    """Envoyer un email de confirmation d'activation"""
    try:
        demande = membre.demande_adhesion if hasattr(membre, 'demande_adhesion') else None
        
        context = {
            'membre': membre,
            'site_name': 'BETA-Résilience',
            'site_url': settings.SITE_URL,
        }
        
        sujet = '✅ Votre compte BETA-Résilience est activé !'
        message_html = render_to_string('membres/email_confirmation_activation.html', context)
        
        admin_nom = request.user.get_full_name() if request and request.user.is_authenticated else ''
        ip_admin = request.META.get('REMOTE_ADDR', '') if request else ''
        
        email = EmailMessage(
            sujet,
            message_html,
            settings.DEFAULT_FROM_EMAIL or 'contact@beta-resilience.org',
            [membre.email],
            reply_to=[settings.CONTACT_EMAIL or 'contact@beta-resilience.org'],
        )
        email.content_subtype = 'html'
        
        try:
            email.send(fail_silently=False)
            statut = 'envoye'
            message_erreur = ''
        except Exception as e:
            statut = 'erreur'
            message_erreur = str(e)
        
        enregistrer_historique_email(
            membre=membre,
            demande=demande,
            type_email='confirmation',
            sujet=sujet,
            destinataire=membre.email,
            contenu=message_html,
            statut=statut,
            message_erreur=message_erreur,
            admin_nom=admin_nom,
            ip_admin=ip_admin,
        )
        
        return statut == 'envoye'
        
    except Exception as e:
        return False


# ===== FONCTIONS EXISTANTES POUR LES CARTES =====

def generer_carte_membre_response(membre):
    """Générer la carte de membre PDF (fonction existante)"""
    # Garder le code existant ici
    pass


def envoyer_carte_membre_email(membre):
    """Envoyer la carte de membre par email (fonction existante)"""
    # Garder le code existant ici
    pass


def generer_nom_utilisateur(prenom, nom):
    """
    Générer un nom d'utilisateur unique
    """
    base = f"{prenom.lower()}.{nom.lower()}"
    username = base
    counter = 1
    
    while User.objects.filter(username=username).exists():
        username = f"{base}{counter}"
        counter += 1
    
    return username


def generer_mot_de_passe(longueur=12):
    """
    Générer un mot de passe sécurisé
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(alphabet) for _ in range(longueur))


def envoyer_identifiants_membre(demande, membre):
    """
    Envoyer un email avec les identifiants au nouveau membre
    """
    try:
        # Générer le nom d'utilisateur
        username = generer_nom_utilisateur(demande.prenom, demande.nom)
        
        # Générer le mot de passe
        password = generer_mot_de_passe()
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=demande.email,
            password=password,
            first_name=demande.prenom,
            last_name=demande.nom,
            is_active=True,
        )
        
        # Associer l'utilisateur au membre
        membre.user = user
        membre.mot_de_passe_temporaire = password
        membre.date_acceptation = timezone.now()
        membre.est_compte_active = True
        membre.save()
        
        # Préparer le contexte pour l'email
        context = {
            'demande': demande,
            'membre': membre,
            'username': username,
            'password': password,
            'site_url': settings.SITE_URL,
            'site_name': 'BETA-Résilience',
            'login_url': f"{settings.SITE_URL}/login/",
            'dashboard_url': f"{settings.SITE_URL}/membres/dashboard/",
        }
        
        # Rendre le template HTML
        sujet = '🎉 Bienvenue chez BETA-Résilience - Vos identifiants de connexion'
        message_html = render_to_string('membres/email_identifiants.html', context)
        
        # Créer et envoyer l'email
        email = EmailMessage(
            sujet,
            message_html,
            settings.DEFAULT_FROM_EMAIL or 'contact@beta-resilience.org',
            [demande.email],
            reply_to=[settings.CONTACT_EMAIL or 'contact@beta-resilience.org'],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)
        
        # Marquer comme envoyé
        membre.email_envoye = True
        membre.save()
        
        return True, username, password
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        return False, None, None