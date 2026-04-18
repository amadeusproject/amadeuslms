from .models import UserModuleRole


def has_resource_permission(user, module, *perm_codenames):
  if not user.is_authenticated:
    return False

  if user.is_superuser:
    return True

  user_assignment = (
    UserModuleRole.objects.filter(user=user, module=module)
    .select_related("role")
    .first()
  )

  if user_assignment:
    if user_assignment.role.permissions.filter(codename__in=perm_codenames).exists():
      return True

  if module.parent:
    return has_resource_permission(user, module.parent, *perm_codenames)

  return False
