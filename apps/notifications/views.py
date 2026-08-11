from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import MessagePrive
from apps.comptes.models import Membre

User = get_user_model()


@login_required
def liste(request):
    """Liste des notifications"""
    # Pour l'instant, on affiche une page simple
    return render(request, 'notifications/liste.html')


@login_required
def marquer_toutes_lues(request):
    """Marquer toutes les notifications comme lues"""
    messages.success(request, 'Toutes les notifications ont été marquées comme lues.')
    return redirect('notifications:liste')


@login_required
def preferences(request):
    """Gérer les préférences de notifications"""
    return render(request, 'notifications/preferences.html')


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages as django_messages
from apps.membres.models import Membre
from apps.notifications.models import MessagePrive


@login_required
@user_passes_test(lambda u: u.is_staff)
def messagerie_admin(request, membre_id=None):
    membres = Membre.objects.filter(est_actif=True).order_by('nom', 'prenom')
    membre_selectionne = None
    fil_messages = []

    if membre_id:
        membre_selectionne = get_object_or_404(Membre, pk=membre_id)
        fil_messages = MessagePrive.objects.filter(membre=membre_selectionne)
        fil_messages.filter(expediteur=membre_selectionne.user).update(lu_par_admin=True)

        if request.method == 'POST':
            contenu = request.POST.get('contenu', '').strip()
            fichier = request.FILES.get('fichier')
            if contenu or fichier:
                MessagePrive.objects.create(
                    membre=membre_selectionne,
                    expediteur=request.user,
                    contenu=contenu,
                    fichier=fichier,
                )
                django_messages.success(request, 'Message envoyé.')
                return redirect('notifications:messagerie_admin_membre', membre_id=membre_selectionne.id)

    return render(request, 'notifications/messagerie_admin.html', {
        'membres': membres,
        'membre_selectionne': membre_selectionne,
        'fil_messages': fil_messages,
    })

@login_required
def messagerie_membre(request):
    # 1. Obtenir la liste de tous les autres membres (exclure l'utilisateur actuel)
    membres = User.objects.exclude(id=request.user.id)
    
    # 2. Récupérer l'ID du membre sélectionné (s'il existe)
    membre_selectionne_id = request.GET.get('membre_id') or request.POST.get('membre_id')
    membre_selectionne = None
    conversation = []

    if membre_selectionne_id:
        membre_selectionne = get_object_or_404(User, id=membre_selectionne_id)

        # Envoi d'un nouveau message
        if request.method == 'POST':
            contenu = request.POST.get('contenu')
            if contenu:
                MessagePrive.objects.create(
                    expediteur=request.user,
                    membre=membre_selectionne,  # Ou destinataire=membre_selectionne selon ton modèle
                    contenu=contenu,
                    objet=request.POST.get('objet', 'Sans objet')
                )
                return redirect(f"{request.path}?membre_id={membre_selectionne.id}")

        # 3. Charger les messages échangés entre les deux membres
        conversation = MessagePrive.objects.filter(
            (Q(expediteur=request.user) & Q(membre=membre_selectionne)) |
            (Q(expediteur=membre_selectionne) & Q(membre=request.user))
        ).order_by('date_envoi')

        # Marquer comme lus les messages reçus de ce membre
        MessagePrive.objects.filter(
            expediteur=membre_selectionne, 
            membre=request.user, 
            lu_par_membre=False
        ).update(lu_par_membre=True)

    context = {
        'membres': membres,
        'membre_selectionne': membre_selectionne,
        'conversation': conversation,
    }
    return render(request, 'notifications/messagerie_membre.html', context)
