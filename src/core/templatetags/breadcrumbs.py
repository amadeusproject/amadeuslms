from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def render_breadcrumbs(title, url_name=None, *args, **kwargs):
  if url_name:
    try:
      url = reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
      url = url_name

    return format_html(
      '<li class="breadcrumb-item"><a href="{}">{}</a></li>', url, title
    )

  return format_html(
    '<li class="breadcrumb-item active" aria-current="page">{}</li>', title
  )
