from django.urls import path
from . import views

app_name = 'authentification'

urlpatterns = [
    path('configurer/', views.configurer, name='configurer'),
    path('inscription-privee/', views.inscription_privee, name='inscription_privee'),
]

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('configurer/', views.configurer, name='configurer'),
    path('inscription-privee/', views.inscription_privee, name='inscription_privee'),

    path('mot-de-passe-oublie/', auth_views.PasswordResetView.as_view(
        template_name='authentification/password_reset.html',
        email_template_name='authentification/password_reset_email.html',
        subject_template_name='authentification/password_reset_subject.txt',
        success_url='/auth-2fa/mot-de-passe-oublie/envoye/',
    ), name='password_reset'),

    path('mot-de-passe-oublie/envoye/', auth_views.PasswordResetDoneView.as_view(
        template_name='authentification/password_reset_done.html',
    ), name='password_reset_done'),

    path('reinitialiser/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='authentification/password_reset_confirm.html',
        success_url='/auth-2fa/reinitialiser/termine/',
    ), name='password_reset_confirm'),

    path('reinitialiser/termine/', auth_views.PasswordResetCompleteView.as_view(
        template_name='authentification/password_reset_complete.html',
    ), name='password_reset_complete'),
]
