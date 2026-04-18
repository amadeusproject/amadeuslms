import os

from django.apps import apps
from django.core.management.base import BaseCommand
from django.utils import timezone

MIGRATION_TEMPLATE = """
from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations


def add_module_permissions(apps, schema_editor):
  # Make sure that the app permissions are registered
  app_config = global_apps.get_app_config(target_app)
  create_permissions(app_config, apps)

  Role = apps.get_model("hrbac", "Role")
  Permission = apps.get_model("auth", "Permission")

  target_role = Role.objects.filter(slug="{role_name}").first()

  if not target_role:
    return

  appPermissions = Permission.objects.filter(content_type__app_label="{target_app}")

  target_role.permissions.add(*appPermissions)

def remove_module_permissions(apps, schema_editor):
  Role = apps.get_model("hrbac", "Role")
  Permission = apps.get_model("auth", "Permission")

  target_role = Role.objects.filter(slug="{role_name}").first()

  if not target_role:
    return

  appPermissions = Permission.objects.filter(content_type__app_label="{target_app}")

  target_role.permissions.remove(*appPermissions)

class Migration(migrations.Migration):
  dependencies = [
    ("{current_app}", "{last_migration}"),
  ]

  operations = [
    migrations.RunPython(add_module_permissions, reverse_code=remove_module_permissions)
  ]
"""


class Command(BaseCommand):
  help = "Generate a migration to add or remove permissions for a role"

  def add_arguments(self, parser):
    parser.add_argument(
      "target_app", type=str, help="Target app label to give permissions"
    )
    parser.add_argument(
      "role_name", type=str, help="Role name to receive the permissions"
    )
    parser.add_argument(
      "--app",
      type=str,
      help="App label where the migration will be created (default: target_app)",
    )

  def handle(self, *args, **options):
    target_app = options["target_app"]
    role_name = options["role_name"]
    dest_app = options["app"] or target_app

    app_config = apps.get_app_config(dest_app)
    migrations_dir = os.path.join(app_config.path, "migrations")

    if not os.path.exists(migrations_dir):
      os.makedirs(migrations_dir)

    migration_files = [
      f for f in os.listdir(migrations_dir) if f.endswith(".py") and f[0].isdigit()
    ]
    last_migration = (
      sorted(migration_files)[-1].replace(".py", "") if migration_files else None
    )

    if not last_migration:
      self.stderr.write(
        self.style.ERROR(
          "No previous migration found. You need to generate app migrations first"
        )
      )
      return

    timestamp = timezone.now().strftime("%Y%m%d_%H%M")
    filename = f"{timestamp}_add_permissions_for_{role_name}.py"

    next_num = int(last_migration.split("_")[0]) + 1
    filename = f"{next_num:04d}_{filename}"
    filepath = os.path.join(migrations_dir, filename)

    content = MIGRATION_TEMPLATE.format(
      current_app=dest_app,
      last_migration=last_migration,
      role_name=role_name,
      target_app=target_app,
    )

    with open(filepath, "w", encoding="utf-8") as f:
      f.write(content)

    self.stdout.write(self.style.SUCCESS(f"Created migration: {filename}"))
