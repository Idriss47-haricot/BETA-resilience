import apps.demandes.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demandes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demande',
            name='fichier',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='demandes/%Y/%m/',
                validators=[apps.demandes.models.valider_fichier_demande],
                verbose_name='Document joint',
            ),
        ),
    ]
