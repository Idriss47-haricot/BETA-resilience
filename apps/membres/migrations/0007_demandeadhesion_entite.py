from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        # Cette migration dépend de votre dernière migration existante
        ('membres', '0006_dedupe_membres_par_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='demandeadhesion',
            name='entite',
            field=models.CharField(
                choices=[
                    ('association', 'BETA-Résilience Association'), 
                    ('bureau_etude', "BETA-Résilience Bureau d'étude"), 
                    ('invest', 'BETA-Résilience INVEST'), 
                    ('laboratoire', 'Laboratoire Résilience')
                ], 
                default='association', 
                max_length=20, 
                verbose_name='Entité choisie'
            ),
        ),
    ]
