from functools import wraps

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .gatekeeper import has_resource_permission


def module_permission_required(permissions):
  def decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
      module_id = kwargs.get("pk") or kwargs.get("module_id")
      module = get_object_or_404(ContentType, pk=module_id)

      method = request.method.lower()
      perms = permissions.get(method, [])

      if not has_resource_permission(request.user, module, *perms):
        raise PermissionDenied

      return view_func(request, *args, **kwargs)

    return _wrapped_view

  return decorator
