from django.shortcuts import render

from django.views import generic
from django.db.models import Count
from django.core.urlresolvers import reverse_lazy

from subjects.models import Tag, Subject
from topics.models import Resource
from users.models import User
from django.http import HttpResponse, JsonResponse
from log.models import Log
import operator
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404, redirect

from datetime import date, timedelta, datetime
import calendar
from collections import OrderedDict

from categories.models import Category


class GeneralView(generic.TemplateView):
    template_name = "dashboards/general.html"

    def dispatch(self, request, *args, **kwargs):
       
        if not request.user.is_staff:
            return redirect('dashboards:view_categories')
        return super(GeneralView, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = {}

        context['months'] = [_('January'), _('February'), _('March'), _('April'), _('May'), _('June'), _('July'), _('August'), 
        _('September'), _('October'), _('November'), _('December')]
        
        return context

class CategoryView(generic.TemplateView):
    template_name = "dashboards/category.html"
    
    def dispatch(self, request, *args, **kwargs):
        return super(CategoryView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {}

        context['categories'] = self.categories_associated_with_user(self.request.user)
        
        return context

    def categories_associated_with_user(self, user):
        if user.is_staff:
            categories = Category.objects.all()
        else:
            categories = Category.objects.filter(coordinators__in = [user])
        return categories