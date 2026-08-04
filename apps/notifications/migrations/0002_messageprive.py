import apps.notifications.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membres', '0005_membres_proxy_entites'),
        ('notifications', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MessagePrive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenu', models.TextField(blank=True, verbose_name='Message')),
                ('fichier', models.FileField(blank=True, null=True, upload_to='messages_prives/%Y/%m/', validators=[apps.notifications.models.valider_fichier_message], verbose_name='Pièce jointe')),
                ('date_envoi', models.DateTimeField(auto_now_add=True)),
                ('lu_par_membre', models.BooleanField(default=False)),
                ('lu_par_admin', models.BooleanField(default=False)),
                ('expediteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages_prives_envoyes', to=settings.AUTH_USER_MODEL)),
                ('membre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='membres.membre')),
            ],
            options={
                'verbose_name': 'Message privé',
                'verbose_name_plural': '💬 Messagerie',
                'ordering': ['date_envoi'],
            },
        ),
    ]
