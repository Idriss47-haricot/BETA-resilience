from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q

from apps.membres.models import Membre
from .models import MessagePrive, Notification


@login_required
def liste(request):
    notifications = Notification.objects.filter(utilisateur=request.user).order_by('-date_creation')
    non_lues_count = notifications.filter(est_lue=False).count()
    
    return render(request, 'notifications/liste.html', {
        'notifications': notifications,
        'non_lues_count': non_lues_count,
    })


@login_required
def marquer_toutes_lues(request):
    """Marquer toutes les notifications non lues comme lues"""
    Notification.objects.filter(
        utilisateur=request.user,
        est_lue=False
    ).update(est_lue=True)
    
    messages.success(request, 'Toutes les notifications ont été marquées comme lues.')
    return redirect('notifications:liste')


@login_required
def preferences(request):
    """Gérer les préférences de notifications"""
    return render(request, 'notifications/preferences.html')


@login_required
@user_passes_test(lambda u: u.is_staff)
def messagerie_admin(request, membre_id=None):
    # Tous les membres sont affichés (sans restriction sur est_actif)
    membres = Membre.objects.all().order_by('nom', 'prenom')
    membre_selectionne = None
    fil_messages = []

    if membre_id:
        membre_selectionne = get_object_or_404(Membre, pk=membre_id)
        fil_messages = MessagePrive.objects.filter(membre=membre_selectionne)
        
        # Marquer comme lus par l'admin si l'expéditeur n'est pas l'admin
        fil_messages.exclude(expediteur=request.user).update(lu_par_admin=True)

        if request.method == 'POST':
            contenu = request.POST.get('contenu', '').strip()
            fichier = request.FILES.get('fichier')
            if contenu or fichier:
                # 1. Création du message privé
                MessagePrive.objects.create(
                    membre=membre_selectionne,
                    expediteur=request.user,
                    contenu=contenu,
                    fichier=fichier
                )
                
                # 2. Création de la notification pour le membre destinataire
                if hasattr(membre_selectionne, 'user') and membre_selectionne.user:
                    msg_text = f"L'administration vous a envoyé un message : '{contenu[:50]}...'" if contenu else "L'administration vous a envoyé un fichier."
                    Notification.objects.create(
                        utilisateur=membre_selectionne.user,
                        titre="Nouveau message de l'administration",
                        message=msg_text,
                        type='message',
                        lien="/notifications/mes-messages/"
                    )

                messages.success(request, 'Message envoyé.')
                return redirect('notifications:messagerie_admin_membre', membre_id=membre_selectionne.id)

    return render(request, 'notifications/messagerie_admin.html', {
        'membres': membres,
        'membre_selectionne': membre_selectionne,
        'fil_messages': fil_messages,
    })


@login_required
def messagerie_membre(request):
    # Récupérer ou créer l'instance Membre liée à l'utilisateur actuel
    membre_actuel, _ = Membre.objects.get_or_create(user=request.user)

    # Récupérer uniquement les membres qui possèdent un compte User valide
    membres = (
        Membre.objects.filter(user__isnull=False)
        .exclude(id=membre_actuel.id)
        .select_related('user')
        .order_by('nom', 'prenom')
    )

    membre_selectionne_id = request.GET.get('membre_id') or request.POST.get('membre_id')
    membre_selectionne = None
    conversation = []

    if membre_selectionne_id:
        membre_selectionne = get_object_or_404(
            Membre.objects.select_related('user'), 
            id=membre_selectionne_id
        )

        # Envoi d'un nouveau message
        if request.method == 'POST':
            contenu = request.POST.get('contenu', '').strip()
            fichier = request.FILES.get('fichier')
            if contenu or fichier:
                # 1. Création du message
                MessagePrive.objects.create(
                    expediteur=request.user,
                    membre=membre_selectionne.user,
                    contenu=contenu,
                    fichier=fichier
                )

                # 2. Notification envoyée au destinataire
                if hasattr(membre_selectionne, 'user') and membre_selectionne.user:
                    nom_expediteur = request.user.get_full_name() or request.user.username
                    Notification.objects.create(
                        utilisateur=membre_selectionne.user,
                        titre="Nouveau message privé",
                        message=f"Vous avez reçu un message de {nom_expediteur}.",
                        type='message',
                        lien=f"/notifications/mes-messages/?membre_id={membre_actuel.id}"
                    )

                return redirect(f"{request.path}?membre_id={membre_selectionne.id}")

        # Charger la conversation (fil d'échange entre les deux membres)
        if membre_selectionne.user:
            conversation = MessagePrive.objects.filter(
                (Q(expediteur=request.user) & Q(membre=membre_selectionne)) |
                (Q(expediteur=membre_selectionne.user) & Q(membre=membre_actuel))
            ).select_related('expediteur', 'membre').order_by('date_envoi')

            # Marquer les messages reçus comme lus
            MessagePrive.objects.filter(
                expediteur=membre_selectionne.user,
                membre=membre_actuel,
                lu_par_membre=False
            ).update(lu_par_membre=True)
        else:
            conversation = MessagePrive.objects.filter(
                expediteur=request.user, 
                membre=membre_selectionne
            ).select_related('expediteur', 'membre').order_by('date_envoi')

    context = {
        'membres': membres,
        'membre_selectionne': membre_selectionne,
        'conversation': conversation,
    }
    return render(request, 'notifications/messagerie_membre.html', context)
