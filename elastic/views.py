from django.views import generic
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, reverse_lazy

from braces import views as braces_mixins

from .models import ElasticSearchSettings
from .forms import SettingsForm

class ESSettings(braces_mixins.LoginRequiredMixin, braces_mixins.StaffuserRequiredMixin, generic.UpdateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'elastic/config.html'
    model = ElasticSearchSettings
    form_class = SettingsForm
    success_url = reverse_lazy("subjects:home")

    def get_object(self, queryset = None):
        return ElasticSearchSettings.objects.last()

    def form_valid(self, form):
        form.save()

        messages.success(self.request, _("Elastic Search settings updated successfully!"))

        return super(ESSettings, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ESSettings, self).get_context_data(**kwargs)

        context['title'] = _('Elastic Search Settings')

        return context