from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from apps.membres.models import Membre


def configurer(request):
    return render(request, 'authentification/configurer.html')


def inscription_privee(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not username or not email or not password:
            return render(request, 'authentification/register.html', {
                'error': "Tous les champs sont obligatoires."
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'authentification/register.html', {
                'error': "Ce nom d'utilisateur est déjà pris."
            })

        membre, cree = Membre.objects.get_or_create(
            email=email,
            defaults={'nom': '', 'prenom': ''}
        )

        if membre.user:
            user = membre.user
            user.username = username
            user.email = email
            user.set_password(password)
            user.save()
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            membre.user = user

        membre.est_compte_active = True
        membre.save()

        login(request, user)
        messages.success(request, f"Bienvenue {username} ! Votre compte est activé.")
        return redirect('membres:dashboard')

    return render(request, 'authentification/register.html')
