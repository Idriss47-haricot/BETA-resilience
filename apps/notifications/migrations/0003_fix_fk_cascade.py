from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_messageprive'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- 1. Supprime la contrainte actuelle bloquante
            ALTER TABLE notifications_messageprive 
            DROP CONSTRAINT IF EXISTS notifications_messageprive_membre_id_fkey;

            -- 2. Pointe vers la vraie table membres_membre avec ON DELETE CASCADE
            ALTER TABLE notifications_messageprive 
            ADD CONSTRAINT notifications_messageprive_membre_id_fkey 
            FOREIGN KEY (membre_id) REFERENCES membres_membre(id) ON DELETE CASCADE;
            """,
            reverse_sql="""
            ALTER TABLE notifications_messageprive 
            DROP CONSTRAINT IF EXISTS notifications_messageprive_membre_id_fkey;
            """
        ),
    ]
