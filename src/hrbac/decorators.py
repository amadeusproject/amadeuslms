from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .gatekeeper import has_resource_permission


def object_permission_required(model_class, permissions):
  if isinstance(permissions, str):
    permissions = [permissions]

  def decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
      pk = kwargs.get("pk") or kwargs.get(f"{model_class._meta.model_name}_id")
      module_object = get_object_or_404(model_class, pk=pk)

      if not has_resource_permission(request.user, module_object, *permissions):
        raise PermissionDenied

      kwargs["permission_object"] = module_object

      return view_func(request, *args, **kwargs)

    return _wrapped_view

  return decorator
