from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations


def add_module_permissions(apps, schema_editor):
  app_config = global_apps.get_app_config("hrbac")
  create_permissions(app_config, verbosity=0)

  Role = apps.get_model("hrbac", "Role")
  Permission = apps.get_model("auth", "Permission")

  target_role = Role.objects.filter(slug="admin").first()

  if not target_role:
    return

  appPermissions = Permission.objects.filter(content_type__app_label="hrbac")

  target_role.permissions.add(*appPermissions)


def remove_module_permissions(apps, schema_editor):
  Role = apps.get_model("hrbac", "Role")
  Permission = apps.get_model("auth", "Permission")

  target_role = Role.objects.filter(slug="admin").first()

  if not target_role:
    return

  appPermissions = Permission.objects.filter(content_type__app_label="hrbac")

  target_role.permissions.remove(*appPermissions)


class Migration(migrations.Migration):
  dependencies = [
    ("hrbac", "0003_auto_20260405_1646"),
  ]

  operations = [
    migrations.RunPython(add_module_permissions, reverse_code=remove_module_permissions)
  ]
