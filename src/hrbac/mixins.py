from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .gatekeeper import has_resource_permission


class ModulePermissionMixin:
  module_method_perms = {}
  module_perm_required = None
  module_model = ContentType

  def get_module_object(self):
    module_id = self.kwargs.get("pk") or self.kwargs.get("module_id")
    return get_object_or_404(self.module_model, pk=module_id)

  def dispatch(self, request, *args, **kwargs):
    module = self.get_module_object()
    method = self.request.method.lower()

    perms = self.module_method_perms.get(method, [])

    if perms is None:
      perms = self.module_perm_required

    if isinstance(perms, str):
      perms = [perms]

    if not has_resource_permission(request.user, module, *perms):
      raise PermissionDenied

    self.module = module
    return super().dispatch(request, *args, **kwargs)
