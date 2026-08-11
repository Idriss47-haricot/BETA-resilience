"""
Vues pour l'application Événements
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from apps.evenements.models import Evenement, InscriptionEvenement
from apps.notifications.models import Notification, MessagePrive
from apps.membres.models import Membre


@login_required
def inscrire_evenement(request, evenement_id):
    """Inscription via ID d'événement avec notification admin"""
    evenement = get_object_or_404(Evenement, pk=evenement_id)
    membre_actuel, _ = Membre.objects.get_or_create(user=request.user)

    inscription, created = InscriptionEvenement.objects.get_or_create(
        evenement=evenement,
        utilisateur=request.user,
        defaults={'statut': 'confirme'}
    )

    if created:
        if hasattr(evenement, 'places_restantes') and evenement.places_restantes is not None:
            evenement.places_restantes = max(0, evenement.places_restantes - 1)
            evenement.save(update_fields=['places_restantes'])

        messages.success(request, "Votre inscription à l'événement a bien été prise en compte.")

        # Notification à tous les administrateurs
        admins = Membre.objects.filter(user__is_staff=True)
        nom_membre = f"{membre_actuel.nom} {membre_actuel.prenom}".strip() or request.user.username
        contenu_notif = f"Le membre {nom_membre} s'est inscrit à l'événement '{evenement.titre}'."

        for admin in admins:
            MessagePrive.objects.create(
                expediteur=request.user,
                membre=admin,
                contenu=contenu_notif
            )
            Notification.objects.create(
                membre=admin,
                titre="Nouvelle inscription à un événement",
                message=contenu_notif,
                type_notif='evenement'
            )
    else:
        messages.info(request, "Vous êtes déjà inscrit à cet événement.")

    return redirect('evenements:detail', slug=evenement.slug)


def liste(request):
    """Liste publique des événements à venir"""
    evenements = Evenement.objects.filter(
        est_publie=True,
        date_debut__gte=timezone.now()
    ).order_by('date_debut')

    evenements_passes = Evenement.objects.filter(
        est_publie=True,
        date_debut__lt=timezone.now()
    ).order_by('-date_debut')[:6]

    return render(request, 'evenements/liste.html', {
        'evenements': evenements,
        'evenements_passes': evenements_passes,
    })


def detail(request, slug):
    """Détail d'un événement"""
    evenement = get_object_or_404(Evenement, slug=slug, est_publie=True)

    est_inscrit = False
    if request.user.is_authenticated:
        est_inscrit = InscriptionEvenement.objects.filter(
            evenement=evenement,
            utilisateur=request.user
        ).exists()

    return render(request, 'evenements/detail.html', {
        'evenement': evenement,
        'est_inscrit': est_inscrit,
    })


@login_required
def mes_evenements(request):
    """Espace membre : événements à venir + inscriptions du membre"""

    # Marquer les notifications d'événements comme lues
    membre_actuel, _ = Membre.objects.get_or_create(user=request.user)
    Notification.objects.filter(
        membre=membre_actuel,
        type_notif='evenement',
        est_lue=False,
    ).update(est_lue=True)

    # Tous les événements publiés à venir
    evenements_a_venir = Evenement.objects.filter(
        est_publie=True,
        date_debut__gte=timezone.now()
    ).order_by('date_debut')

    # Inscriptions du membre connecté
    mes_inscriptions = InscriptionEvenement.objects.filter(
        utilisateur=request.user
    ).select_related('evenement').order_by('-evenement__date_debut')

    ids_inscrits = set(
        mes_inscriptions.values_list('evenement_id', flat=True)
    )

    return render(request, 'evenements/mes_evenements.html', {
        'evenements_a_venir': evenements_a_venir,
        'mes_inscriptions': mes_inscriptions,
        'ids_inscrits': ids_inscrits,
    })


@login_required
def s_inscrire(request, slug):
    """Inscrire le membre connecté à un événement via slug"""
    evenement = get_object_or_404(Evenement, slug=slug, est_publie=True)
    membre_actuel, _ = Membre.objects.get_or_create(user=request.user)

    if hasattr(evenement, 'places_restantes') and evenement.places_restantes is not None and evenement.places_restantes <= 0:
        messages.error(request, '❌ Plus de places disponibles pour cet événement.')
        return redirect('evenements:detail', slug=slug)

    inscription, created = InscriptionEvenement.objects.get_or_create(
        evenement=evenement,
        utilisateur=request.user,
        defaults={'statut': 'confirme'}
    )

    if created:
        if hasattr(evenement, 'places_restantes') and evenement.places_restantes is not None:
            evenement.places_restantes = max(0, evenement.places_restantes - 1)
            evenement.save(update_fields=['places_restantes'])

        messages.success(request, f'✅ Inscription confirmée pour "{evenement.titre}" !')

        # Notification aux admins
        admins = Membre.objects.filter(user__is_staff=True)
        nom_membre = f"{membre_actuel.nom} {membre_actuel.prenom}".strip() or request.user.username
        contenu_notif = f"Le membre {nom_membre} s'est inscrit à l'événement '{evenement.titre}'."

        for admin in admins:
            MessagePrive.objects.create(
                expediteur=request.user,
                membre=admin,
                contenu=contenu_notif
            )
            Notification.objects.create(
                membre=admin,
                titre="Nouvelle inscription à un événement",
                message=contenu_notif,
                type_notif='evenement'
            )
    else:
        messages.info(request, 'ℹ️ Vous êtes déjà inscrit à cet événement.')

    return redirect('evenements:mes_evenements')


@login_required
def se_desinscrire(request, slug):
    """Désinscrire le membre connecté d'un événement"""
    evenement = get_object_or_404(Evenement, slug=slug)

    deleted, _ = InscriptionEvenement.objects.filter(
        evenement=evenement,
        utilisateur=request.user
    ).delete()

    if deleted:
        if hasattr(evenement, 'places_restantes') and evenement.places_restantes is not None:
            evenement.places_restantes += 1
            evenement.save(update_fields=['places_restantes'])
        messages.success(request, f'✅ Désinscription effectuée pour "{evenement.titre}".')
    else:
        messages.warning(request, "⚠️ Vous n'étiez pas inscrit à cet événement.")

    return redirect('evenements:mes_evenements')


@login_required
def annuler_inscription(request, slug):
    """Annuler l'inscription à un événement"""
    evenement = get_object_or_404(Evenement, slug=slug)
    inscription = get_object_or_404(InscriptionEvenement, evenement=evenement, utilisateur=request.user)

    inscription.delete()
    if hasattr(evenement, 'places_restantes') and evenement.places_restantes is not None:
        evenement.places_restantes += 1
        evenement.save(update_fields=['places_restantes'])

    messages.success(request, f'❌ Inscription à "{evenement.titre}" annulée.')
    return redirect('evenements:detail', slug=evenement.slug)
