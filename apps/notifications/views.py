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