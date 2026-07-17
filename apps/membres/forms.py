"""
Formulaires de l'application Membres
"""
from django import forms
from django.core.validators import FileExtensionValidator
from apps.membres.models import DemandeAdhesion, Membre
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re
from apps.membres.models import Membre



class ActivationForm(UserCreationForm):
    """
    Formulaire d'activation de compte
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Choisissez un nom d\'utilisateur'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Mot de passe (min 8 caractères)'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmez votre mot de passe'
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise forms.ValidationError('Le mot de passe doit contenir au moins 8 caractères.')
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('Le mot de passe doit contenir au moins une majuscule.')
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError('Le mot de passe doit contenir au moins un chiffre.')
        return password


class DemandeAdhesionForm(forms.ModelForm):
    """
    Formulaire de demande d'adhésion
    """
    class Meta:
        model = DemandeAdhesion
        fields = [
            'nom', 'prenom', 'email', 'telephone', 'date_naissance',
            'profession', 'motivation', 'competences', 'cv', 'lettre_motivation'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'motivation': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Pourquoi souhaitez-vous rejoindre BETA-Résilience ?'}),
            'competences': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Décrivez vos compétences et domaines d\'expertise...'}),
        }
        labels = {
            'cv': 'Curriculum Vitae (PDF ou DOC)',
            'lettre_motivation': 'Lettre de motivation (optionnelle)',
        }
        help_texts = {
            'cv': 'Formats acceptés : PDF, DOC, DOCX (max 5 Mo)',
            'lettre_motivation': 'Formats acceptés : PDF, DOC, DOCX (max 5 Mo)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs requis
        self.fields['nom'].required = True
        self.fields['prenom'].required = True
        self.fields['email'].required = True
        self.fields['telephone'].required = True
        self.fields['motivation'].required = True
    
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            # Nettoyer le numéro
            telephone = re.sub(r'[^0-9+]', '', telephone)
            if len(telephone) < 8:
                raise forms.ValidationError('Le numéro de téléphone est trop court.')
        return telephone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Vérifier si l'email est déjà utilisé
            if DemandeAdhesion.objects.filter(email=email, statut='acceptee').exists():
                raise forms.ValidationError('Cet email est déjà associé à un membre.')
        return email
    
    def clean_cv(self):
        cv = self.cleaned_data.get('cv')
        if cv:
            # Vérifier la taille du fichier
            if cv.size > 5 * 1024 * 1024:  # 5 Mo
                raise forms.ValidationError('Le fichier ne doit pas dépasser 5 Mo.')
            
            # Vérifier l'extension
            ext = cv.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx']:
                raise forms.ValidationError('Seuls les fichiers PDF, DOC et DOCX sont acceptés.')
        return cv
    
    def clean_lettre_motivation(self):
        lettre = self.cleaned_data.get('lettre_motivation')
        if lettre:
            if lettre.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Le fichier ne doit pas dépasser 5 Mo.')
            
            ext = lettre.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx']:
                raise forms.ValidationError('Seuls les fichiers PDF, DOC et DOCX sont acceptés.')
        return lettre


class MembreRegistrationForm(UserCreationForm):
    """
    Formulaire d'inscription pour les membres (accès à l'espace membre)
    """
    email = forms.EmailField(required=True)
    nom = forms.CharField(max_length=100, required=True)
    prenom = forms.CharField(max_length=100, required=True)
    telephone = forms.CharField(max_length=50, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'nom', 'prenom', 'telephone', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Créer le profil membre
            Membre.objects.create(
                user=user,
                nom=self.cleaned_data['nom'],
                prenom=self.cleaned_data['prenom'],
                email=self.cleaned_data['email'],
                telephone=self.cleaned_data.get('telephone', ''),
                est_actif=True
            )
        return user
    

class ProfilMembreForm(forms.ModelForm):
    """
    Formulaire de modification du profil membre
    """
    class Meta:
        model = Membre
        fields = ['nom', 'prenom', 'telephone', 'biographie', 'photo']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre téléphone'}),
            'biographie': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Parlez-nous de vous...'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nom': 'Nom',
            'prenom': 'Prénom',
            'telephone': 'Téléphone',
            'biographie': 'Biographie',
            'photo': 'Photo de profil',
        }