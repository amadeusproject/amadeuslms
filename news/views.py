from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from log.models import Log
from log.mixins import LogMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _


from .models import News
from .forms import NewsForm

class VisualizeNews(LoginRequiredMixin,LogMixin,generic.ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'news/view.html'
    context_object_name = "new"

    def get_context_data(self, **kwargs):
        context = super(VisualizeNews, self).get_context_data(**kwargs)
        context['title'] = _('Visualize News')

        return context

    def get_queryset(self):
        slug = self.kwargs.get('slug', '')
        new = News.objects.get(slug=slug)

        return new

class ListNewsView(LoginRequiredMixin,LogMixin,generic.ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'news/list.html'
    context_object_name = "news"
    paginate_by = 10

    def get_queryset(self):
        news = News.objects.all().order_by('create_date')

        return news

    def get_context_data(self, **kwargs):
        context = super(ListNewsView, self).get_context_data(**kwargs)
        context['title'] = _('Manage News')

        return context


class CreateNewsView(LoginRequiredMixin,LogMixin,generic.edit.CreateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'news/create.html'
    form_class = NewsForm

    def form_valid(self, form):
        self.object = form.save(commit = False)
        creator = self.request.user
        self.object.creator = creator

        self.object.save()

        return super(CreateNewsView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _('News successfully created!'))

        return reverse_lazy('news:view', kwargs = {'slug': self.object.slug} )

    def get_context_data (self, **kwargs):
        context = super(CreateNewsView, self).get_context_data(**kwargs)
        context['title'] = _("Create News")

        return context

class UpdateNewsView(LoginRequiredMixin,LogMixin,generic.UpdateView):
        login_url = reverse_lazy("users:login")
        redirect_field_name = 'next'
        template_name = 'news/update.html'
        form_class = NewsForm
        model = News

        def get_success_url(self):
            messages.success(self.request, _('News successfully created!'))

            return reverse_lazy('news:view', kwargs = {'slug': self.object.slug} )

        def get_context_data (self, **kwargs):
            context = super(UpdateNewsView, self).get_context_data(**kwargs)
            context['title'] = _("Update News")

            return context

        def form_valid(self, form):
            self.object = form.save(commit = False)
            creator = self.request.user
            self.object.creator = creator

            self.object.save()

            return super(UpdateNewsView, self).form_valid(form)
