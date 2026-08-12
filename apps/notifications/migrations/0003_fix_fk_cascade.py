from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_messageprive'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- 1. Supprime la contrainte SQL stricte vers auth_user
            ALTER TABLE notifications_messageprive 
            DROP CONSTRAINT IF EXISTS notifications_messageprive_membre_id_fkey;

            -- 2. Ré-ajoute la contrainte avec CASCADE
            ALTER TABLE notifications_messageprive 
            ADD CONSTRAINT notifications_messageprive_membre_id_fkey 
            FOREIGN KEY (membre_id) REFERENCES auth_user(id) ON DELETE CASCADE;
            """,
            reverse_sql="""
            ALTER TABLE notifications_messageprive 
            DROP CONSTRAINT IF EXISTS notifications_messageprive_membre_id_fkey;
            """
        ),
    ]
