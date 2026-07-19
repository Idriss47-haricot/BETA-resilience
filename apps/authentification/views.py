from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from apps.membres.models import Membre


def configurer(request):
    return render(request, 'authentification/configurer.html')


def inscription_privee(request):
    token = request.GET.get('token') or request.POST.get('token')

    membre = None
    if token:
        membre = Membre.objects.filter(token_activation=token).first()

    if not membre or not membre.verifier_token_activation(token):
        return render(request, 'authentification/register.html', {
            'error': "Ce lien d'inscription est invalide ou a expiré. Contactez un administrateur."
        })

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not username or not email or not password:
            return render(request, 'authentification/register.html', {
                'error': "Tous les champs sont obligatoires."
            })

        user = membre.user
        user.username = username
        user.email = email
        user.set_password(password)
        user.save()

        membre.est_compte_active = True
        membre.token_activation = ''
        membre.save(update_fields=['est_compte_active', 'token_activation'])

        login(request, user)
        messages.success(request, f"Bienvenue {username} ! Votre compte est activé.")
        return redirect('membres:dashboard')

    return render(request, 'authentification/register.html')
