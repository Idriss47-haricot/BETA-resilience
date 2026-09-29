"""
Administration de l'application Événements
"""
from django import forms
from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from apps.core.admin import admin_site
from apps.evenements.models import Evenement, InscriptionEvenement
from apps.notifications.models import Notification
from .models import Evenement


class EvenementAdminForm(forms.ModelForm):
    """Formulaire personnalisé avec widgets pour les dates"""

    date_debut = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'vDateTimeField'},
            format='%Y-%m-%dT%H:%M',
        ),
        input_formats=[
            '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M',
            '%d/%m/%Y %H:%M',
        ],
        label='Date de début',
    )

    date_fin = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'vDateTimeField'},
            format='%Y-%m-%dT%H:%M',
        ),
        input_formats=[
            '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M',
            '%d/%m/%Y %H:%M',
        ],
        label='Date de fin',
        required=False,
    )

    class Meta:
        model = Evenement
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            now = timezone.localtime(timezone.now())
            rounded = now.replace(minute=0, second=0, microsecond=0)
            if now.minute >= 30:
                rounded += timezone.timedelta(hours=1)
            self.fields['date_debut'].initial = rounded.replace(tzinfo=None)
            self.fields['date_fin'].initial = (
                rounded + timezone.timedelta(hours=2)
            ).replace(tzinfo=None)
        else:
            if self.instance.date_debut:
                self.fields['date_debut'].initial = timezone.localtime(
                    self.instance.date_debut
                ).replace(tzinfo=None)
            if self.instance.date_fin:
                self.fields['date_fin'].initial = timezone.localtime(
                    self.instance.date_fin
                ).replace(tzinfo=None)


class InscriptionEvenementInline(admin.TabularInline):
    model = InscriptionEvenement
    extra = 0
    fields = ('utilisateur', 'statut', 'date_inscription')
    readonly_fields = ('date_inscription',)


@admin.register(Evenement, site=admin_site)
class EvenementAdmin(admin.ModelAdmin):
    form = EvenementAdminForm
    list_display = ('titre', 'date_debut', 'date_fin', 'lieu', 'statut', 'places_restantes')
    list_filter = ('statut', 'est_publie', 'date_debut')
    search_fields = ('titre', 'description', 'lieu')
    prepopulated_fields = {'slug': ('titre',)}
    ordering = ('date_debut',)
    inlines = [InscriptionEvenementInline]

    fieldsets = (
        ('📝 Informations', {
            'fields': ('titre', 'slug', 'type_evenement', 'description', 'programme')
        }),
        ('📅 Dates et lieu', {
            'fields': ('date_debut', 'date_fin', 'lieu', 'adresse')
        }),
        ('👥 Capacité', {
            'fields': ('capacite_max', 'places_restantes')
        }),
        ('📷 Image', {
            'fields': ('image',)
        }),
        ('📊 Statut', {
            'fields': ('statut', 'est_publie')
        }),
        ('💰 Prix', {
            'fields': ('est_gratuit', 'prix')
        }),
        ('👨‍🏫 Intervenants', {
            'fields': ('intervenants',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
    actions = ['notifier_membres']

    # =========================================================
    # FIX PRINCIPAL : save_model déclenche notifs + mails
    # automatiquement à la CRÉATION de l'événement
    # =========================================================
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # change=False → nouvelle création ; change=True → modification
        if not change and obj.est_publie:
            nb_notifs, nb_mails = self._notifier_tous_membres(obj)
            self.message_user(
                request,
                f'✅ Événement créé — {nb_notifs} notification(s) et {nb_mails} email(s) envoyés.'
            )

    # =========================================================
    # Méthode partagée entre save_model et l'action manuelle
    # =========================================================
    def _notifier_tous_membres(self, evenement):
        from apps.membres.models import Membre

        membres = Membre.objects.filter(
            est_actif=True,
            est_compte_active=True,
            user__isnull=False,
        ).select_related('user')

        date_str = timezone.localtime(evenement.date_debut).strftime('%d/%m/%Y à %H:%M')
        nb_notifs = 0
        nb_mails  = 0

        for membre in membres:
            user = membre.user

            # ── 1. Notification en base ──────────────────────
            Notification.objects.get_or_create(
                utilisateur=user,
                type='evenement_ajoute',
                titre=f'📅 Nouvel événement : {evenement.titre}',
                defaults={
                    'message': (
                        f'Un nouvel événement "{evenement.titre}" est programmé '
                        f'le {date_str}.\n'
                        f'Lieu : {evenement.lieu or "À confirmer"}'
                    ),
                    'lien': evenement.get_absolute_url(),
                }
            )
            nb_notifs += 1

            # ── 2. Email ─────────────────────────────────────
            email_dest = user.email or membre.email
            if not email_dest:
                continue

            # Vérifier les préférences de notification si elles existent
            try:
                prefs = user.preferences_notifications
                if not prefs.email_notifications:
                    continue
            except Exception:
                pass  # Pas de préférences → on envoie quand même

            sujet = f'[BETA-Résilience] 📅 Nouvel événement : {evenement.titre}'
            corps = f"""Bonjour {membre.prenom} {membre.nom},

Un nouvel événement a été organisé par BETA-Résilience :

📌 {evenement.titre}
📅 Le {date_str}
📍 Lieu : {evenement.lieu or 'À confirmer'}
{f"📝 {evenement.description[:300]}..." if evenement.description else ""}

Connectez-vous à votre espace membre pour plus de détails et pour vous inscrire :
{settings.SITE_URL}{evenement.get_absolute_url()}

Cordialement,
L'équipe BETA-Résilience
"""
            try:
                send_mail(
                    subject=sujet,
                    message=corps,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email_dest],
                    fail_silently=False,
                )
                nb_mails += 1
            except Exception as e:
                # Log l'erreur sans bloquer les autres envois
                print(f'[BETA] Erreur mail → {email_dest} : {e}')

        return nb_notifs, nb_mails

    # =========================================================
    # Action manuelle (déclenchée depuis la liste admin)
    # =========================================================
    def notifier_membres(self, request, queryset):
        total_notifs = 0
        total_mails  = 0
        for evenement in queryset:
            n, m = self._notifier_tous_membres(evenement)
            total_notifs += n
            total_mails  += m

        self.message_user(
            request,
            f'✅ {total_notifs} notification(s) et {total_mails} email(s) envoyés '
            f'pour {queryset.count()} événement(s).'
        )
    notifier_membres.short_description = '📧 Notifier les membres de cet événement'


@admin.register(InscriptionEvenement, site=admin_site)
class InscriptionEvenementAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'evenement', 'statut', 'date_inscription')
    list_filter = ('statut', 'evenement')
    search_fields = ('utilisateur__username', 'evenement__titre')