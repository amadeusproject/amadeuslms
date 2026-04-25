from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .gatekeeper import has_global_permission, has_resource_permission


class GlobalPermissionMixin:
  method_permissions = {}

  def dispatch(self, request, *args, **kwargs):
    method = request.method.lower()
    perms = self.method_permissions.get(method, [])

    if isinstance(perms, str):
      perms = [perms]

    if not has_global_permission(request.user, *perms):
      raise PermissionDenied

    return super().dispatch(request, *args, **kwargs)


class ModulePermissionMixin:
  module_method_perms = {}

  def get_permission_object(self):
    if hasattr(self, "get_object"):
      return self.get_object()

    model_class = getattr(self, "model", None)

    pk = self.kwargs.get("pk") or self.kwargs.get(f"{model_class._meta.model_name}_id")
    return get_object_or_404(model_class, pk=pk)

  def dispatch(self, request, *args, **kwargs):
    module_object = self.get_permission_object()
    method = request.method.lower()

    perms = self.module_method_perms.get(method, [])

    if isinstance(perms, str):
      perms = [perms]

    if not has_resource_permission(request.user, module_object, *perms):
      raise PermissionDenied

    self.permission_object = module_object
    return super().dispatch(request, *args, **kwargs)
