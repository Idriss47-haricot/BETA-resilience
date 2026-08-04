from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect


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
    try:
        membre = Membre.objects.get(user=request.user)
    except Membre.DoesNotExist:
        django_messages.error(request, "Aucune fiche membre associée à votre compte.")
        return redirect('membres:dashboard')

    fil_messages = MessagePrive.objects.filter(membre=membre)
    fil_messages.filter(expediteur__is_staff=True).update(lu_par_membre=True)

    if request.method == 'POST':
        contenu = request.POST.get('contenu', '').strip()
        fichier = request.FILES.get('fichier')
        if contenu or fichier:
            MessagePrive.objects.create(
                membre=membre,
                expediteur=request.user,
                contenu=contenu,
                fichier=fichier,
            )
            return redirect('notifications:messagerie_membre')

    return render(request, 'notifications/messagerie_membre.html', {
        'membre': membre,
        'fil_messages': fil_messages,
    })
