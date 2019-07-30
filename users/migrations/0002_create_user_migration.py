from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth import get_user_model


def create_admin_user(apps, schema_editor):
    User = apps.get_model("users", "User")
    db_alias = schema_editor.connection.alias
    new_admin_user = get_user_model().objects.create_user(email="admin@amadeus.com",
                                                          password="admin",
                                                          username="admin",
                                                          last_name="admin",
                                                          is_staff=True)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin_user, migrations.RunPython.noop),
    ]
