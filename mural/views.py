from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count

from .models import GeneralPost, CategoryPost, SubjectPost, MuralVisualizations

class GeneralIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/list.html'
	model = GeneralPost
	context_object_name = "posts"
	paginate_by = 10

	totals = {}

	def get_queryset(self):
		user = self.request.user

		general = GeneralPost.objects.all()
		
		self.totals['general'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__generalpost__isnull = False) | Q(comment__post__generalpost__isnull = False))).distinct().count()
		self.totals['category'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__categorypost__space__coordinators = user) | Q(comment__post__categorypost__space__coordinators = user) | Q(post__categorypost__space__subject_category__professor = user) | Q(post__categorypost__space__subject_category__students = user) | Q(comment__post__categorypost__space__subject_category__professor = user) | Q(comment__post__categorypost__space__subject_category__students = user))).distinct().count()
		self.totals['subject'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__subjectpost__space__professor = user) | Q(comment__post__subjectpost__space__professor = user) | Q(post__subjectpost__space__students = user) | Q(comment__post__subjectpost__space__students = user))).distinct().count()

		return general

	def get_context_data(self, **kwargs):
		context = super(GeneralIndex, self).get_context_data(**kwargs)

		context['title'] = _('Mural')
		context['totals'] = self.totals
		context['mural_menu_active'] = 'subjects_menu_active'

		return context
