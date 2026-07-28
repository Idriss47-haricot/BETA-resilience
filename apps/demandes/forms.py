"""
Formulaires de l'application Demandes
"""
from django import forms
from apps.demandes.models import Demande
import re


class DemandeForm(forms.ModelForm):
    """
    Formulaire de soumission de demande
    """
    class Meta:
        model = Demande
        fields = [
            'entite', 'type_demande', 'autre_type',
            'nom', 'prenom', 'email', 'telephone',
            'societe', 'fonction',
            'objet', 'message', 'fichier'
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Décrivez votre demande en détail...'}),
            'objet': forms.TextInput(attrs={'placeholder': 'Sujet de votre demande'}),
            'autre_type': forms.TextInput(attrs={'placeholder': 'Précisez votre type de demande'}),
            'nom': forms.TextInput(attrs={'placeholder': 'Votre nom'}),
            'prenom': forms.TextInput(attrs={'placeholder': 'Votre prénom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'votre@email.com'}),
            'telephone': forms.TextInput(attrs={'placeholder': '6XX-XXX-XXX'}),
            'societe': forms.TextInput(attrs={'placeholder': 'Nom de votre société ou institution (optionnel)'}),
            'fonction': forms.TextInput(attrs={'placeholder': 'Votre fonction (optionnel)'}),
        }
        labels = {
            'entite': 'Entité concernée',
            'type_demande': 'Type de demande',
            'autre_type': 'Autre type (précisez)',
            'societe': 'Société / Institution',
            'fonction': 'Fonction',
            'fichier': 'Document joint (optionnel)',
        }
        help_texts = {
            'fichier': 'Formats acceptés : PDF, DOC, DOCX (max 5 Mo)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Marquer les champs requis
        self.fields['nom'].required = True
        self.fields['prenom'].required = True
        self.fields['email'].required = True
        self.fields['telephone'].required = True
        self.fields['objet'].required = True
        self.fields['message'].required = True
        
        # Masquer le champ autre_type par défaut
        self.fields['autre_type'].widget.attrs['style'] = 'display: none;'
        
        # Définir les types de demande par entité
        self.type_choices = {
            'association': [
                ('adhesion', 'Adhésion'),
                ('benefice', 'Bénévolat'),
                ('don', 'Don'),
                ('partenariat', 'Partenariat associatif'),
                ('information', 'Demande d\'information'),
            ],
            'bureau_etude': [
                ('etude', 'Étude environnementale'),
                ('expertise', 'Expertise technique'),
                ('conseil', 'Conseil stratégique'),
                ('formation', 'Formation'),
                ('prestation', 'Prestation de service'),
            ],
            'invest': [
                ('investissement', 'Investissement'),
                ('partenariat', 'Partenariat économique'),
                ('financement', 'Financement de projet'),
                ('conseil', 'Conseil en investissement'),
            ],
            'laboratoire': [
                ('collaboration', 'Collaboration scientifique'),
                ('recherche', 'Projet de recherche'),
                ('publication', 'Publication scientifique'),
                ('stage', 'Stage / Recherche'),
                ('partenariat', 'Partenariat académique'),
            ],
        }
        
        # Définir les choix initiaux du type_demande
        initial_entite = self.initial.get('entite', '')
        if initial_entite in self.type_choices:
            self.fields['type_demande'].choices = self.type_choices[initial_entite]
        else:
            self.fields['type_demande'].choices = [('', 'Sélectionnez une entité d\'abord')]
    
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            telephone = re.sub(r'[^0-9+]', '', telephone)
            if len(telephone) < 8:
                raise forms.ValidationError('Le numéro de téléphone est trop court.')
        return telephone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                raise forms.ValidationError('Veuillez saisir une adresse email valide.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        entite = cleaned_data.get('entite')
        type_demande = cleaned_data.get('type_demande')
        autre_type = cleaned_data.get('autre_type')
        
        if entite and type_demande == 'autre' and not autre_type:
            self.add_error('autre_type', 'Veuillez préciser votre type de demande.')
        
        return cleaned_data