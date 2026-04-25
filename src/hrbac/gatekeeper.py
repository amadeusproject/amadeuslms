from django.contrib.contenttypes.models import ContentType

from .models import UserGlobalRole, UserModuleRole


def has_global_permission(user, *perm_codenames):
  if not user.is_authenticated:
    return False

  if user.is_superuser:
    return True

  return UserGlobalRole.objects.filter(
    user=user, role__permissions__codename__in=perm_codenames
  ).exists()


def has_resource_permission(user, module_object, *perm_codenames):
  if has_global_permission(user, *perm_codenames):
    return True

  if not module_object:
    return False

  content_type = ContentType.objects.get_for_model(module_object)

  user_assignment = (
    UserModuleRole.objects.filter(
      user=user, module=content_type, object_id=module_object
    )
    .select_related("role")
    .first()
  )

  if user_assignment:
    if user_assignment.role.permissions.filter(codename__in=perm_codenames).exists():
      return True

  if hasattr(module_object, "access_parent") and module_object.access_parent:
    return has_resource_permission(user, module_object.access_parentt, *perm_codenames)

  return False
