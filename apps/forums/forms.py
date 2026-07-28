"""
Formulaires pour l'application Forums
"""
from django import forms
from apps.forums.models import ForumSujet, ForumMessage


class SujetForm(forms.ModelForm):
    """
    Formulaire de création d'un nouveau sujet
    """
    contenu = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Rédigez votre message...'
        }),
        label='Contenu du message'
    )
    
    class Meta:
        model = ForumSujet
        fields = ['titre', 'contenu']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du sujet'
            }),
        }
        labels = {
            'titre': 'Titre du sujet',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titre'].required = True
        self.fields['contenu'].required = True


class MessageForm(forms.ModelForm):
    """
    Formulaire de réponse à un sujet
    """
    class Meta:
        model = ForumMessage
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Rédigez votre réponse...'
            }),
        }
        labels = {
            'contenu': 'Votre message',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contenu'].required = True


class RechercheForumForm(forms.Form):
    """
    Formulaire de recherche dans les forums
    """
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher dans les forums...'
        }),
        label=''
    )