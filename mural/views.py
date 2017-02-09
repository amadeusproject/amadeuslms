from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count

from channels import Group
import json

from users.models import User

from .models import Mural, GeneralPost, CategoryPost, SubjectPost, MuralVisualizations, MuralFavorites, Comment
from .forms import GeneralPostForm, CommentForm

class GeneralIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/list.html'
	context_object_name = "posts"
	paginate_by = 10

	totals = {}

	def get_queryset(self):
		user = self.request.user
		favorites = self.request.GET.get('favorite', False)
		mines = self.request.GET.get('mine', False)
		showing = self.request.GET.get('showing', False)
		page = self.request.GET.get('page', False)

		if not favorites:
			if mines:
				general = GeneralPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_generalpost.mural_ptr_id))"}).filter(mural_ptr__user = user)
			else:
				general = GeneralPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_generalpost.mural_ptr_id))"})
		else:
			if mines:
				general = GeneralPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_generalpost.mural_ptr_id))"}).filter(favorites_post__isnull = False, favorites_post__user = user, mural_ptr__user = user)
			else:
				general = GeneralPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_generalpost.mural_ptr_id))"}).filter(favorites_post__isnull = False, favorites_post__user = user)

		if showing: #Exclude ajax creation posts results
			showing = showing.split(',')
			general = general.exclude(id__in = showing)

		if not page: #Don't need this if is pagination
			general_visualizations = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__generalpost__isnull = False) | Q(comment__post__generalpost__isnull = False))).distinct()

			self.totals['general'] = general_visualizations.count()
			self.totals['category'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__categorypost__space__coordinators = user) | Q(comment__post__categorypost__space__coordinators = user) | Q(post__categorypost__space__subject_category__professor = user) | Q(post__categorypost__space__subject_category__students = user) | Q(comment__post__categorypost__space__subject_category__professor = user) | Q(comment__post__categorypost__space__subject_category__students = user))).distinct().count()
			self.totals['subject'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__subjectpost__space__professor = user) | Q(comment__post__subjectpost__space__professor = user) | Q(post__subjectpost__space__students = user) | Q(comment__post__subjectpost__space__students = user))).distinct().count()

			general_visualizations.update(viewed = True)

		return general.order_by("-most_recent")

	def get_context_data(self, **kwargs):
		context = super(GeneralIndex, self).get_context_data(**kwargs)

		page = self.request.GET.get('page', '')

		if page:
			self.template_name = "mural/_list_view.html"

		context['title'] = _('Mural')
		context['totals'] = self.totals
		context['mural_menu_active'] = 'subjects_menu_active'
		context['favorites'] = ""
		context['mines'] = ""

		favs = self.request.GET.get('favorite', False)

		if favs:
			context['favorites'] = "checked"

		mines = self.request.GET.get('mine', False)

		if mines:
			context['mines'] = "checked"

		return context

class GeneralCreate(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/_form.html'
	form_class = GeneralPostForm

	def form_invalid(self, form):
		context = super(GeneralCreate, self).form_invalid(form)
		context.status_code = 400

		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)

		self.object.user = self.request.user

		self.object.save()

		users = User.objects.all().exclude(id = self.request.user.id)
		entries = []

		notify_type = "mural"
		user_icon = self.object.user.image_url
		_view = render_to_string("mural/_view.html", {"post": self.object}, self.request)
		simple_notify = _("%s has made a post in General")%(str(self.object.user))
		pathname = reverse("mural:manage_general")

		for user in users:
			entries.append(MuralVisualizations(viewed = False, user = user, post = self.object))
			Group("user-%s" % user.id).send({'text': json.dumps({"type": notify_type, "subtype": "create", "user_icon": user_icon, "pathname": pathname, "simple": simple_notify, "complete": _view})})

		MuralVisualizations.objects.bulk_create(entries)

		return super(GeneralCreate, self).form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super(GeneralCreate, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:create_general")

		return context

	def get_success_url(self):
		return reverse_lazy('mural:render_post_general', args = (self.object.id, 'create', ))

class GeneralUpdate(LoginRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/_form.html'
	model = GeneralPost
	form_class = GeneralPostForm

	def form_invalid(self, form):
		context = super(GeneralUpdate, self).form_invalid(form)
		context.status_code = 400

		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)

		self.object.edited = True

		self.object.save()

		users = User.objects.all().exclude(id = self.request.user.id)
		
		notify_type = "mural"
		_view = render_to_string("mural/_view.html", {"post": self.object}, self.request)
		pathname = reverse("mural:manage_general")

		for user in users:
			Group("user-%s" % user.id).send({'text': json.dumps({"type": notify_type, "subtype": "update", "pathname": pathname, "complete": _view, "post_id": self.object.id})})
		
		return super(GeneralUpdate, self).form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super(GeneralUpdate, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:update_general", args = (), kwargs = {'pk': self.object.id})

		return context

	def get_success_url(self):
		return reverse_lazy('mural:render_post_general', args = (self.object.id, 'update', ))

class GeneralDelete(LoginRequiredMixin, generic.DeleteView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/delete.html'
	model = GeneralPost

	def get_context_data(self, *args, **kwargs):
		context = super(GeneralDelete, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:delete_general", args = (), kwargs = {'pk': self.object.id})

		return context

	def get_success_url(self):
		users = User.objects.all().exclude(id = self.request.user.id)
		
		notify_type = "mural"
		pathname = reverse("mural:manage_general")

		for user in users:
			Group("user-%s" % user.id).send({'text': json.dumps({"type": notify_type, "subtype": "delete", "pathname": pathname, "post_id": self.object.id})})

		return reverse_lazy('mural:deleted_post')	

def render_gen_post(request, post, msg):
	post = get_object_or_404(GeneralPost, id = post)

	context = {}
	context['post'] = post

	msg = ""

	if msg == 'create':
		msg = _('Your post was published successfully!')
	else:
		msg = _('Your post was edited successfully!')

	html = render_to_string("mural/_view.html", context, request)

	return JsonResponse({'message': msg, 'view': html, 'new_id': post.id})

def deleted_post(request):
	return JsonResponse({'msg': _('Post deleted successfully!')})

@login_required
def favorite(request, post):
	action = request.GET.get('action', '')
	post = get_object_or_404(Mural, id = post)

	if action == 'favorite':
		MuralFavorites.objects.create(post = post, user = request.user)

		return JsonResponse({'label': _('Unfavorite')})
	else:
		MuralFavorites.objects.filter(post = post, user = request.user).delete()

		return JsonResponse({'label': _('Favorite')})

class CommentCreate(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/_form_comment.html'
	form_class = CommentForm

	def form_invalid(self, form):
		context = super(CommentCreate, self).form_invalid(form)
		context.status_code = 400

		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)

		post_id = self.kwargs.get('post', '')
		post = get_object_or_404(Mural, id = post_id)

		self.object.user = self.request.user
		self.object.post = post

		self.object.save()

		users = User.objects.all().exclude(id = self.request.user.id)
		entries = []

		notify_type = "mural"
		user_icon = self.object.user.image_url
		#_view = render_to_string("mural/_view.html", {"post": self.object}, self.request)
		simple_notify = _("%s has made a post in General")%(str(self.object.user))
		pathname = reverse("mural:manage_general")

		#for user in users:
		#	entries.append(MuralVisualizations(viewed = False, user = user, post = self.object))
		#	Group("user-%s" % user.id).send({'text': json.dumps({"type": notify_type, "subtype": "create", "user_icon": user_icon, "pathname": pathname, "simple": simple_notify, "complete": _view})})

		#MuralVisualizations.objects.bulk_create(entries)

		return super(CommentCreate, self).form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super(CommentCreate, self).get_context_data(*args, **kwargs)

		post_id = self.kwargs.get('post', '')

		context['form_url'] = reverse_lazy("mural:create_comment", kwargs = {"post": post_id})

		return context

	def get_success_url(self):
		return reverse_lazy('mural:render_comment', args = (self.object.id, 'create', ))

def render_comment(request, comment, msg):
	comment = get_object_or_404(Comment, id = comment)

	context = {}
	context['comment'] = comment

	msg = ""

	if msg == 'create':
		msg = _('Your comment was published successfully!')
	else:
		msg = _('Your comment was edited successfully!')

	html = render_to_string("mural/_view_comment.html", context, request)

	return JsonResponse({'message': msg, 'view': html, 'new_id': comment.id})