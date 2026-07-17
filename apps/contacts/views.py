"""
Vues de l'application Contacts - Version complète
"""
from django.views.generic import FormView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import requests
import json

from apps.contacts.forms import ContactForm
from apps.contacts.models import MessageContact


class ContactView(FormView):
    """
    Formulaire de contact avec reCAPTCHA et email
    """
    template_name = 'contacts/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contacts:contact_succes')
    
    def form_valid(self, form):
        # Vérifier reCAPTCHA
        recaptcha_response = self.request.POST.get('g-recaptcha-response')
        if not self.verifier_recaptcha(recaptcha_response):
            messages.error(self.request, 'Veuillez valider le captcha.')
            return self.form_invalid(form)
        
        # Sauvegarder le message
        message = form.save(commit=False)
        message.ip_address = self.request.META.get('REMOTE_ADDR', '')
        message.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        message.save()
        
        # Envoyer la notification par email
        self.envoyer_email_notification(message)
        
        messages.success(
            self.request,
            'Votre message a été envoyé avec succès. '
            'Nous vous répondrons dans les plus brefs délais.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Veuillez corriger les erreurs ci-dessous.')
        return super().form_invalid(form)
    
    def verifier_recaptcha(self, recaptcha_response):
        """
        Vérifier le reCAPTCHA avec l'API Google
        """
        if not recaptcha_response:
            return False
        
        # En production, utilisez la clé secrète depuis les variables d'environnement
        secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', '')
        if not secret_key:
            # Si pas de clé, on considère le captcha comme valide (pour le développement)
            return True
        
        try:
            payload = {
                'secret': secret_key,
                'response': recaptcha_response,
            }
            response = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data=payload,
                timeout=5
            )
            result = response.json()
            return result.get('success', False)
        except Exception:
            return True  # En cas d'erreur, on laisse passer pour ne pas bloquer
    
    def envoyer_email_notification(self, message):
        """
        Envoyer une notification par email à l'administrateur
        """
        try:
            sujet = f'[BETA-Résilience] Nouveau message de {message.prenom} {message.nom}'
            
            context = {
                'message': message,
                'site_name': settings.SITE_NAME,
                'admin_url': settings.ADMIN_URL,
            }
            
            message_html = render_to_string('contacts/email_notification.html', context)
            
            email = EmailMessage(
                sujet,
                message_html,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                reply_to=[message.email],
            )
            email.content_subtype = 'html'
            email.send(fail_silently=True)
        except Exception as e:
            print(f"Erreur d'envoi d'email: {e}")


class ContactSuccesView(TemplateView):
    """Page de confirmation de contact"""
    template_name = 'contacts/contact_succes.html'