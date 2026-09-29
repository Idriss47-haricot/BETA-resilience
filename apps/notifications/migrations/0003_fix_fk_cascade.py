# apps/notifications/migrations/0003_fix_fk_cascade.py

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_messageprive'),
    ]

    operations = [
        # SQLite ne supporte pas ALTER TABLE ... ADD/DROP CONSTRAINT.
        # On laisse les opérations vides ou prises en charge par ORM/SchemaEditor.
    ]