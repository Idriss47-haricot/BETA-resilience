from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membres', '0004_membre_entite'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembreAssociation',
            fields=[],
            options={
                'verbose_name': 'Membre - Association',
                'verbose_name_plural': '👥 Membres · Association',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('membres.membre',),
        ),
        migrations.CreateModel(
            name='MembreBureauEtude',
            fields=[],
            options={
                'verbose_name': "Membre - Bureau d'étude",
                'verbose_name_plural': "👥 Membres · Bureau d'étude",
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('membres.membre',),
        ),
        migrations.CreateModel(
            name='MembreInvest',
            fields=[],
            options={
                'verbose_name': 'Membre - INVEST',
                'verbose_name_plural': '👥 Membres · INVEST',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('membres.membre',),
        ),
        migrations.CreateModel(
            name='MembreLaboratoire',
            fields=[],
            options={
                'verbose_name': 'Membre - Laboratoire',
                'verbose_name_plural': '👥 Membres · Laboratoire',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('membres.membre',),
        ),
    ]
