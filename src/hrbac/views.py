from django.contrib import messages
from django.contrib.auth.models import Permission
from django.http import HttpResponse, QueryDict
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from .models import Role


class RoleMatrixView(TemplateView):
  template_name = "hrbac/role_matrix.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    context["title"] = _("Permissões")

    roles = Role.objects.all().order_by("id").prefetch_related("permissions")

    excluded_apps = ["admin", "contenttypes", "sessions", "auth"]

    all_perms = (
      Permission.objects.exclude(content_type__app_label__in=excluded_apps)
      .select_related("content_type")
      .order_by("content_type__app_label", "codename")
    )
    perms_by_model = {}

    for perm in all_perms:
      model_name = (
        perm.content_type.model_class()._meta.verbose_name.capitalize()
        if perm.content_type.model_class()
        else perm.content_type.model
      )

      if model_name not in perms_by_model:
        perms_by_model[model_name] = {"perms": [], "ct_id": perm.content_type.id}

      perms_by_model[model_name]["perms"].append(perm)

    for model_info in perms_by_model.values():
      model_perms_ids = set(p.id for p in model_info["perms"])
      for role in roles:
        role_perms_ids = set(p.id for p in role.permissions.all())

        setattr(
          role,
          f"all_checked_{model_info['ct_id']}",
          model_perms_ids.issubset(role_perms_ids),
        )

    context["roles"] = roles
    context["permissions_by_model"] = perms_by_model

    return context

  def get(self, request, *args, **kwargs):
    edit_role_id = request.GET.get("edit_role_id")

    if edit_role_id:
      role = get_object_or_404(Role, id=edit_role_id)

      action = request.GET.get("action")

      if action == "cancel_edit":
        return TemplateResponse(
          request, "hrbac/partials/_role_header.html", {"role": role}
        )

      return TemplateResponse(
        request, "hrbac/partials/_role_edit_header.html", {"role": role}
      )

    return super().get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    name = request.POST.get("role_name")

    if name:
      Role.objects.create(name=name)

      messages.success(request, _("Perfil criado com sucesso"))

    return HttpResponse(status=204, headers={"HX-Refresh": "true"})

  def patch(self, request, *args, **kwargs):
    data = QueryDict(request.body)
    role = get_object_or_404(Role, id=data.get("role_id"))

    if "role_name" in data:
      new_name = data.get("role_name")

      if new_name and new_name != role.name:
        role.name = new_name
        role.save()

      return TemplateResponse(
        request, "hrbac/partials/_role_header.html", {"role": role}
      )

    if data.get("perm_id"):
      perm = get_object_or_404(Permission, id=data.get("perm_id"))
      if role.permissions.filter(id=perm.id).exists():
        role.permissions.remove(perm)
      else:
        role.permissions.add(perm)

    elif data.get("content_type_id"):
      ct_id = data.get("content_type_id")
      action = request.POST.get("action")
      perms = Permission.objects.filter(content_type_id=ct_id)

      if action == "add":
        role.permissions.add(*perms)
      elif action == "remove":
        role.permissions.remove(*perms)

    messages.success(request, _("Permissões atualizadas com sucesso"))

    return HttpResponse(status=200)

  def delete(self, request, *args, **kwargs):
    role_id = request.GET.get("role_id")
    role = get_object_or_404(Role, id=role_id)
    role.delete()
    messages.success(request, _("Perfil deletado com sucesso"))
    return HttpResponse(status=200, headers={"HX-Refresh": "true"})
