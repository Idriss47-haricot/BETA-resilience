from django.db import migrations


def dedupliquer_membres(apps, schema_editor):
    Membre = apps.get_model('membres', 'Membre')

    emails_vus = {}
    for membre in Membre.objects.all().order_by('id'):
        email = (membre.email or '').strip().lower()
        if not email:
            continue
        if email not in emails_vus:
            emails_vus[email] = membre
        else:
            garde = emails_vus[email]
            # Si le doublon a un compte utilisateur lié et pas l'original, on garde celui avec le compte
            if membre.user_id and not garde.user_id:
                emails_vus[email] = membre
                garde, membre = membre, garde
            membre.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('membres', '0005_membres_proxy_entites'),
    ]

    operations = [
        migrations.RunPython(dedupliquer_membres, migrations.RunPython.noop),
    ]
