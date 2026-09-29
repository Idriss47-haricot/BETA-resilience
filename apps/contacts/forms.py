"""
Formulaires de l'application Contacts
"""
from django import forms
from apps.contacts.models import MessageContact
from django.core.validators import RegexValidator
import re


class ContactForm(forms.ModelForm):
    """
    Formulaire de contact avec validation
    """
    # Champ honeypot pour anti-spam
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)
    
    class Meta:
        model = MessageContact
        fields = ['nom', 'prenom', 'email', 'telephone', 'sujet', 'sujet_personnalise', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Votre message...'}),
            'sujet_personnalise': forms.TextInput(attrs={'placeholder': 'Précisez votre sujet si "Autre"'}),
        }
        labels = {
            'sujet_personnalise': 'Sujet personnalisé',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marquer les champs requis
        self.fields['nom'].required = True
        self.fields['prenom'].required = True
        self.fields['email'].required = True
        self.fields['message'].required = True
        
        # Ajouter des placeholders
        self.fields['nom'].widget.attrs['placeholder'] = 'Votre nom'
        self.fields['prenom'].widget.attrs['placeholder'] = 'Votre prénom'
        self.fields['email'].widget.attrs['placeholder'] = 'votre@email.com'
        self.fields['telephone'].widget.attrs['placeholder'] = 'Votre numéro de téléphone'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Vérifier si l'email est valide
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                raise forms.ValidationError('Veuillez saisir une adresse email valide.')
        return email
    
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            # Nettoyer le numéro
            telephone = re.sub(r'[^0-9+]', '', telephone)
            if len(telephone) < 8:
                raise forms.ValidationError('Le numéro de téléphone est trop court.')
        return telephone
    
    def clean_honeypot(self):
        honeypot = self.cleaned_data.get('honeypot')
        if honeypot:
            raise forms.ValidationError('Spam détecté.')
        return honeypot
    
    def clean(self):
        cleaned_data = super().clean()
        sujet = cleaned_data.get('sujet')
        sujet_personnalise = cleaned_data.get('sujet_personnalise')
        
        if sujet == 'autre' and not sujet_personnalise:
            self.add_error('sujet_personnalise', 'Veuillez préciser votre sujet.')
        
        return cleaned_data