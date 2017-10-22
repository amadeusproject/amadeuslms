""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from log.models import Log
from log.mixins import LogMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q, Count

from .models import News, valid_formats
from .forms import NewsForm

class VisualizeNews(LoginRequiredMixin,LogMixin,generic.ListView):
    log_action = "view_new"
    log_resource = "news"
    log_component = "news"
    log_context = {}

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

        self.log_context['new_title'] = new.title
        self.log_context['new_slug'] = new.slug

        super(VisualizeNews, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return new

class ListNewsView(LoginRequiredMixin,LogMixin,generic.ListView):
    log_action = "view_list_of_news"
    log_resource = "news"
    log_component = "news"
    log_context = {}


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

        super(ListNewsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return context


class CreateNewsView(LoginRequiredMixin,LogMixin,generic.edit.CreateView):
    log_action = "create"
    log_resource = "news"
    log_component = "news"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'news/create.html'
    form_class = NewsForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(reverse_lazy('subjects:home'))
        return super(CreateNewsView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit = False)
        creator = self.request.user
        self.object.creator = creator

        self.object.save()

        self.log_context['new_creator_user'] = self.object.creator.get_short_name()
        self.log_context['new_title'] = self.object.title
        self.log_context['new_slug'] = self.object.slug

        super(CreateNewsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return super(CreateNewsView, self).form_valid(form)

    def get_context_data (self, **kwargs):
        context = super(CreateNewsView, self).get_context_data(**kwargs)
        context['title'] = _("Create News")
        context['mimeTypes'] = valid_formats

        return context
    
    def get_success_url(self):
        messages.success(self.request, _('News successfully created!'))

        return reverse_lazy('news:view', kwargs = {'slug': self.object.slug} )

class UpdateNewsView(LoginRequiredMixin,LogMixin,generic.UpdateView):
    log_action = "update"
    log_resource = "news"
    log_component = "news"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'news/update.html'
    form_class = NewsForm
    model = News

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(reverse_lazy('subjects:home'))
        return super(UpdateNewsView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit = False)
        creator = self.request.user
        self.object.creator = creator

        self.object.save()

        self.log_context['new_update_user'] = self.object.creator.get_short_name()
        self.log_context['new_title'] = self.object.title
        self.log_context['new_slug'] = self.object.slug

        super(UpdateNewsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return super(UpdateNewsView, self).form_valid(form)
    
    def get_context_data (self, **kwargs):
        context = super(UpdateNewsView, self).get_context_data(**kwargs)
        context['title'] = _("Update News")
        context['mimeTypes'] = valid_formats

        return context

    def get_success_url(self):
        messages.success(self.request, _('News successfully updated!'))

        return reverse_lazy('news:view', kwargs = {'slug': self.object.slug} )

class SearchNewsView(LoginRequiredMixin, LogMixin, generic.ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'news/search.html'
    context_object_name = 'news'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
    	search = self.request.GET.get('search', '')

    	if search == '':
    		return redirect(reverse_lazy('news:manage_news'))

    	return super(SearchNewsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        inteiro = False

        search = self.request.GET.get('search', '')
        print(type(search))
        try:
            search = int(search)
            inteiro = True
        except Exception as e:
            inteiro = False

        if inteiro:
            news = News.objects.filter(Q(title__icontains = search) | Q(creator__username__icontains = search) | Q(create_date__icontains = search)  | Q(create_date__year = search) | Q(create_date__month = search)  | Q(create_date__day = search) ).distinct().order_by('create_date')
        else:
            news = News.objects.filter(Q(title__icontains = search) | Q(creator__username__icontains = search) | Q(create_date__icontains = search) ).distinct().order_by('create_date')


        return news

    def get_context_data (self, **kwargs):
    	context = super(SearchNewsView, self).get_context_data(**kwargs)
    	context['title'] = _('Search News')
    	context['search'] = self.request.GET.get('search')

    	return context

class DeleteNewsView(LoginRequiredMixin,LogMixin,generic.DeleteView):
    log_component = 'news'
    log_action = 'delete'
    log_resource = 'news'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    model = News
    template_name = 'news/delete.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(reverse_lazy('subjects:home'))
        return super(DeleteNewsView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        news = get_object_or_404(News, slug = self.kwargs.get('slug'))
        return super(DeleteNewsView, self).delete(self, request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, _('News "%s" removed successfully!')%(self.object.title))
        success_url = reverse_lazy('news:manage_news')

        return success_url

    def get_context_data(self, **kwargs):
        context = super(DeleteNewsView, self).get_context_data(**kwargs)
        context['title'] = _('Delete News')
        news = get_object_or_404(News, slug = self.kwargs.get('slug'))
        context['new'] = news

        self.log_context['new_creator'] = news.creator.get_short_name()
        self.log_context['new_title'] = news.title
        self.log_context['new_slug'] = news.slug

        super(DeleteNewsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return context
