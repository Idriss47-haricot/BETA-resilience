# Generated manually for notifications app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MessagePrive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('objet', models.CharField(blank=True, max_length=255, verbose_name='Objet')),
                ('contenu', models.TextField(verbose_name='Contenu')),
                ('date_envoi', models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")),
                ('lu_par_membre', models.BooleanField(default=False, verbose_name='Lu par le membre')),
                ('lu_par_admin', models.BooleanField(default=False, verbose_name='Lu par l admin')),
                ('destinataire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages_recus', to=settings.AUTH_USER_MODEL, verbose_name='Destinataire')),
                ('expediteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages_envoyes', to=settings.AUTH_USER_MODEL, verbose_name='Expéditeur')),
            ],
            options={
                'verbose_name': 'Message privé',
                'verbose_name_plural': 'Messages privés',
                'ordering': ['-date_envoi'],
            },
        ),
    ]
