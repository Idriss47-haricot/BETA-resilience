"""
Formulaires de l'application Actualités
"""
from django import forms
from apps.actualites.models import Commentaire
import re


class CommentaireForm(forms.ModelForm):
    """
    Formulaire de commentaire
    """
    class Meta:
        model = Commentaire
        fields = ['auteur', 'email', 'site_web', 'contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Votre commentaire...'}),
            'auteur': forms.TextInput(attrs={'placeholder': 'Votre nom'}),
            'email': forms.TextInput(attrs={'placeholder': 'votre@email.com'}),
            'site_web': forms.TextInput(attrs={'placeholder': 'https://votre-site.com (optionnel)'}),
        }
        labels = {
            'auteur': 'Nom complet',
            'site_web': 'Site web (optionnel)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['auteur'].required = True
        self.fields['email'].required = True
        self.fields['contenu'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                raise forms.ValidationError('Veuillez saisir une adresse email valide.')
        return email
    
    def clean_site_web(self):
        site_web = self.cleaned_data.get('site_web')
        if site_web and not site_web.startswith(('http://', 'https://')):
            site_web = 'https://' + site_web
        return site_web