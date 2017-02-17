from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
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

from categories.models import Category
from subjects.models import Subject
from users.models import User

from .models import Mural, GeneralPost, CategoryPost, SubjectPost, MuralVisualizations, MuralFavorites, Comment
from .forms import GeneralPostForm, CategoryPostForm, SubjectPostForm, CommentForm
from .utils import getSpaceUsers

"""
	Section for GeneralPost classes
"""
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
			self.totals['category'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & ((Q(user__is_staff = True) & (Q(post__categorypost__isnull = False) | Q(comment__post__categorypost__isnull = False))) | Q(post__categorypost__space__coordinators = user) | Q(comment__post__categorypost__space__coordinators = user) | Q(post__categorypost__space__subject_category__students = user) | Q(comment__post__categorypost__space__subject_category__students = user) | Q(post__categorypost__space__subject_category__professor = user) | Q(comment__post__categorypost__space__subject_category__professor = user))).distinct().count()
			self.totals['subject'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & ((Q(user__is_staff = True) & (Q(post__subjectpost__isnull = False) | Q(comment__post__subjectpost__isnull = False))) | Q(post__subjectpost__space__professor = user) | Q(comment__post__subjectpost__space__professor = user) | Q(post__subjectpost__space__students = user) | Q(comment__post__subjectpost__space__students = user))).distinct().count()
			
			general_visualizations.update(viewed = True)

			MuralVisualizations.objects.filter(user = user, viewed = False, comment__post__generalpost__isnull = False).update(viewed = True)

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

		paths = [reverse("mural:manage_general")]

		notification = {
			"type": "mural",
			"subtype": "post",
			"paths": paths,
			"user_icon": self.object.user.image_url,
			"simple_notify": _("%s has made a post in General")%(str(self.object.user)),
			"complete": render_to_string("mural/_view.html", {"post": self.object}, self.request),
			"container": ".post", 
			"accordion": False
		}

		notification = json.dumps(notification)

		for user in users:
			entries.append(MuralVisualizations(viewed = False, user = user, post = self.object))
			Group("user-%s" % user.id).send({'text': notification})

		MuralVisualizations.objects.bulk_create(entries)

		return super(GeneralCreate, self).form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super(GeneralCreate, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:create_general")

		return context

	def get_success_url(self):
		return reverse_lazy('mural:render_post', args = (self.object.id, 'create', 'gen', ))

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
		
		paths = [reverse("mural:manage_general")]

		notification = {
			"type": "mural",
			"subtype": "mural_update",
			"paths": paths,
			"complete": render_to_string("mural/_view.html", {"post": self.object}, self.request),
			"container": "#post-" + str(self.object.id),
		}

		notification = json.dumps(notification)

		for user in users:
			Group("user-%s" % user.id).send({'text': notification})
		
		return super(GeneralUpdate, self).form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super(GeneralUpdate, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:update_general", args = (), kwargs = {'pk': self.object.id})

		return context

	def get_success_url(self):
		return reverse_lazy('mural:render_post', args = (self.object.id, 'update', 'gen', ))

class GeneralDelete(LoginRequiredMixin, generic.DeleteView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/delete.html'
	model = GeneralPost

	def get_context_data(self, *args, **kwargs):
		context = super(GeneralDelete, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:delete_general", args = (), kwargs = {'pk': self.object.id})
		context['message'] = _('Are you sure you want to delete this post?')

		return context

	def get_success_url(self):
		users = User.objects.all().exclude(id = self.request.user.id)
				
		paths = [reverse("mural:manage_general")]

		notification = {
			"type": "mural",
			"subtype": "mural_delete",
			"paths": paths,
			"container": "#post-" + str(self.object.id),
		}

		notification = json.dumps(notification)

		for user in users:
			Group("user-%s" % user.id).send({'text': notification})

		return reverse_lazy('mural:deleted_post')

"""
	Section for CategoryPost classes
"""
def load_category_posts(request, category):
	context = {
		'request': request,
	}

	user = request.user
	favorites = request.GET.get('favorite', False)
	mines = request.GET.get('mine', False)
	showing = request.GET.get('showing', '')
	n_views = 0
	
	if not favorites:
		if mines:
			posts = CategoryPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_categorypost.mural_ptr_id))"}).filter(space__id = category, mural_ptr__user = user)
		else:
			posts = CategoryPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_categorypost.mural_ptr_id))"}).filter(space__id = category)
	else:
		if mines:
			posts = CategoryPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_categorypost.mural_ptr_id))"}).filter(space__id = category, favorites_post__isnull = False, favorites_post__user = user, mural_ptr__user = user)
		else:
			posts = CategoryPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_categorypost.mural_ptr_id))"}).filter(space__id = category, favorites_post__isnull = False, favorites_post__user = user)
	
	if showing: #Exclude ajax creation posts results
		showing = showing.split(',')
		posts = posts.exclude(id__in = showing)

	has_page = request.GET.get('page', None)

	if has_page is None:
		views = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(comment__post__categorypost__space__id = category) | Q(post__categorypost__space__id = category)))
		n_views = views.count()
		views.update(viewed = True)

	paginator = Paginator(posts.order_by("-most_recent"), 10)

	try:
		page_number = int(request.GET.get('page', 1))
	except ValueError:
		raise Http404

	try:
		page_obj = paginator.page(page_number)
	except EmptyPage:
		raise Http404

	context['posts'] = page_obj.object_list

	response = render_to_string("mural/_list_view.html", context, request)

	return JsonResponse({"posts": response, "unviewed": n_views, "count": posts.count(), "num_pages": paginator.num_pages, "num_page": page_obj.number})

class CategoryIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/list_category.html'
	context_object_name = "categories"
	paginate_by = 10

	totals = {}

	def get_queryset(self):
		user = self.request.user
		
		if user.is_staff:
			categories = Category.objects.all()
		else:
			categories = Category.objects.filter(Q(coordinators__pk = user.pk) | Q(subject_category__professor__pk = user.pk) | Q(subject_category__students__pk = user.pk, visible = True)).distinct()

		self.totals['general'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__generalpost__isnull = False) | Q(comment__post__generalpost__isnull = False))).distinct().count()
		self.totals['category'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & ((Q(user__is_staff = True) & (Q(post__categorypost__isnull = False) | Q(comment__post__categorypost__isnull = False))) | Q(post__categorypost__space__coordinators = user) | Q(comment__post__categorypost__space__coordinators = user) | Q(post__categorypost__space__subject_category__students = user) | Q(comment__post__categorypost__space__subject_category__students = user) | Q(post__categorypost__space__subject_category__professor = user) | Q(comment__post__categorypost__space__subject_category__professor = user))).distinct().count()
		self.totals['subject'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & ((Q(user__is_staff = True) & (Q(post__subjectpost__isnull = False) | Q(comment__post__subjectpost__isnull = False))) | Q(post__subjectpost__space__professor = user) | Q(comment__post__subjectpost__space__professor = user) | Q(post__subjectpost__space__students = user) | Q(comment__post__subjectpost__space__students = user))).distinct().count()

		return categories

	def get_context_data(self, **kwargs):
		context = super(CategoryIndex, self).get_context_data(**kwargs)

		context['title'] = _('Mural - Per Category')
		context['totals'] = self.totals
		context['mural_menu_active'] = 'subjects_menu_active'
		
		return context

class CategoryCreate(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/_form.html'
	form_class = CategoryPostForm

	def form_invalid(self, form):
		context = super(CategoryCreate, self).form_invalid(form)
		context.status_code = 400

		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)

		slug = self.kwargs.get('slug', None)
		cat = get_object_or_404(Category, slug = slug)

		self.object.space = cat
		self.object.user = self.request.user

		self.object.save()

		users = getSpaceUsers(self.request.user.id, self.object)
		entries = []
		
		paths = [reverse("mural:manage_category")]

		notification = {
			"type": "mural",
			"subtype": "post",
			"paths": paths,
			"user_icon": self.object.user.image_url,
			"simple_notify": _("%s has made a post in %s")%(str(self.object.user), str(self.object.space)),
			"complete": render_to_string("mural/_view.html", {"post": self.object}, self.request),
			"container": "#" + slug, 
			"accordion": True
		}

		notification = json.dumps(notification)

		for user in users:
			entries.append(MuralVisualizations(viewed = False, user = user, post = self.object))
			Group("user-%s" % user.id).send({'text': notification})

		MuralVisualizations.objects.bulk_create(entries)

		return super(CategoryCreate, self).form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super(CategoryCreate, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:create_category", args = (), kwargs = {'slug': self.kwargs.get('slug', None)})

		return context

	def get_success_url(self):
		return reverse_lazy('mural:render_post', args = (self.object.id, 'create', 'cat', ))

class CategoryUpdate(LoginRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/_form.html'
	model = CategoryPost
	form_class = CategoryPostForm

	def form_invalid(self, form):
		context = super(CategoryUpdate, self).form_invalid(form)
		context.status_code = 400

		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)

		self.object.edited = True

		self.object.save()

		users = getSpaceUsers(self.request.user.id, self.object)
		
		paths = [reverse("mural:manage_category")]

		notification = {
			"type": "mural",
			"subtype": "mural_update",
			"paths": paths,
			"complete": render_to_string("mural/_view.html", {"post": self.object}, self.request),
			"container": "#post-" + str(self.object.id),
		}

		notification = json.dumps(notification)

		for user in users:
			Group("user-%s" % user.id).send({'text': notification})
		
		return super(CategoryUpdate, self).form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super(CategoryUpdate, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:update_category", args = (), kwargs = {'pk': self.object.id})

		return context

	def get_success_url(self):
		return reverse_lazy('mural:render_post', args = (self.object.id, 'update', 'cat', ))

class CategoryDelete(LoginRequiredMixin, generic.DeleteView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/delete.html'
	model = CategoryPost

	def get_context_data(self, *args, **kwargs):
		context = super(CategoryDelete, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:delete_category", args = (), kwargs = {'pk': self.object.id})
		context['message'] = _('Are you sure you want to delete this post?')

		return context

	def get_success_url(self):
		users = getSpaceUsers(self.request.user.id, self.object)
		
		paths = [reverse("mural:manage_category")]

		notification = {
			"type": "mural",
			"subtype": "mural_delete",
			"paths": paths,
			"container": "#post-" + str(self.object.id),
		}

		notification = json.dumps(notification)

		for user in users:
			Group("user-%s" % user.id).send({'text': notification})

		return reverse_lazy('mural:deleted_post')

"""
	Section for SubjectPost classes
"""
def load_subject_posts(request, subject):
	context = {
		'request': request,
	}

	user = request.user
	favorites = request.GET.get('favorite', False)
	mines = request.GET.get('mine', False)
	showing = request.GET.get('showing', '')
	n_views = 0
	
	if not favorites:
		if mines:
			posts = SubjectPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_subjectpost.mural_ptr_id))"}).filter(space__id = subject, mural_ptr__user = user)
		else:
			posts = SubjectPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_subjectpost.mural_ptr_id))"}).filter(space__id = subject)
	else:
		if mines:
			posts = SubjectPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_subjectpost.mural_ptr_id))"}).filter(space__id = subject, favorites_post__isnull = False, favorites_post__user = user, mural_ptr__user = user)
		else:
			posts = SubjectPost.objects.extra(select = {"most_recent": "greatest(last_update, (select max(mural_comment.last_update) from mural_comment where mural_comment.post_id = mural_subjectpost.mural_ptr_id))"}).filter(space__id = subject, favorites_post__isnull = False, favorites_post__user = user)
	
	if showing: #Exclude ajax creation posts results
		showing = showing.split(',')
		posts = posts.exclude(id__in = showing)

	has_page = request.GET.get('page', None)

	if has_page is None:
		views = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(comment__post__subjectpost__space__id = subject) | Q(post__subjectpost__space__id = subject)))
		n_views = views.count()
		views.update(viewed = True)

	paginator = Paginator(posts.order_by("-most_recent"), 10)

	try:
		page_number = int(request.GET.get('page', 1))
	except ValueError:
		raise Http404

	try:
		page_obj = paginator.page(page_number)
	except EmptyPage:
		raise Http404

	context['posts'] = page_obj.object_list

	response = render_to_string("mural/_list_view.html", context, request)

	return JsonResponse({"posts": response, "unviewed": n_views, "count": posts.count(), "num_pages": paginator.num_pages, "num_page": page_obj.number})

class SubjectIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/list_subject.html'
	context_object_name = "subjects"
	paginate_by = 10

	totals = {}

	def get_queryset(self):
		user = self.request.user
		
		if user.is_staff:
			subjects = Subject.objects.all()
		else:
			subjects = Subject.objects.filter(Q(category__coordinators__pk = user.pk) | Q(professor__pk = user.pk) | Q(students__pk = user.pk, visible = True)).distinct()

		self.totals['general'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__generalpost__isnull = False) | Q(comment__post__generalpost__isnull = False))).distinct().count()
		self.totals['category'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & ((Q(user__is_staff = True) & (Q(post__categorypost__isnull = False) | Q(comment__post__categorypost__isnull = False))) | Q(post__categorypost__space__coordinators = user) | Q(comment__post__categorypost__space__coordinators = user) | Q(post__categorypost__space__subject_category__students = user) | Q(comment__post__categorypost__space__subject_category__students = user) | Q(post__categorypost__space__subject_category__professor = user) | Q(comment__post__categorypost__space__subject_category__professor = user))).distinct().count()
		self.totals['subject'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & ((Q(user__is_staff = True) & (Q(post__subjectpost__isnull = False) | Q(comment__post__subjectpost__isnull = False))) | Q(post__subjectpost__space__professor = user) | Q(comment__post__subjectpost__space__professor = user) | Q(post__subjectpost__space__students = user) | Q(comment__post__subjectpost__space__students = user))).distinct().count()

		return subjects

	def get_context_data(self, **kwargs):
		context = super(SubjectIndex, self).get_context_data(**kwargs)

		context['title'] = _('Mural - Per Subject')
		context['totals'] = self.totals
		context['mural_menu_active'] = 'subjects_menu_active'
		
		return context

class SubjectCreate(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/_form.html'
	form_class = SubjectPostForm

	def get_initial(self):
		initial = super(SubjectCreate, self).get_initial()

		slug = self.kwargs.get('slug', None)
		sub = get_object_or_404(Subject, slug = slug)

		initial['subject'] = sub
		initial['user'] = self.request.user

		return initial

	def form_invalid(self, form):
		context = super(SubjectCreate, self).form_invalid(form)
		context.status_code = 400

		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)

		slug = self.kwargs.get('slug', None)
		sub = get_object_or_404(Subject, slug = slug)

		self.object.space = sub
		self.object.user = self.request.user

		self.object.save()

		users = getSpaceUsers(self.request.user.id, self.object)
		entries = []

		paths = [reverse("mural:manage_subject")]

		notification = {
			"type": "mural",
			"subtype": "post",
			"paths": paths,
			"user_icon": self.object.user.image_url,
			"simple_notify": _("%s has made a post in %s")%(str(self.object.user), str(self.object.space)),
			"complete": render_to_string("mural/_view.html", {"post": self.object}, self.request),
			"container": "#" + slug, 
			"accordion": True
		}

		notification = json.dumps(notification)

		for user in users:
			entries.append(MuralVisualizations(viewed = False, user = user, post = self.object))
			Group("user-%s" % user.id).send({'text': notification})

		MuralVisualizations.objects.bulk_create(entries)

		return super(SubjectCreate, self).form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super(SubjectCreate, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:create_subject", args = (), kwargs = {'slug': self.kwargs.get('slug', None)})

		return context

	def get_success_url(self):
		return reverse_lazy('mural:render_post', args = (self.object.id, 'create', 'sub', ))

class SubjectUpdate(LoginRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/_form.html'
	model = SubjectPost
	form_class = SubjectPostForm

	def get_initial(self):
		initial = super(SubjectUpdate, self).get_initial()

		initial['user'] = self.request.user

		return initial

	def form_invalid(self, form):
		context = super(SubjectUpdate, self).form_invalid(form)
		context.status_code = 400

		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)

		self.object.edited = True

		self.object.save()

		users = getSpaceUsers(self.request.user.id, self.object)
		
		paths = [reverse("mural:manage_subject")]

		notification = {
			"type": "mural",
			"subtype": "mural_update",
			"paths": paths,
			"complete": render_to_string("mural/_view.html", {"post": self.object}, self.request),
			"container": "#post-" + str(self.object.id),
		}

		notification = json.dumps(notification)

		for user in users:
			Group("user-%s" % user.id).send({'text': notification})
		
		return super(SubjectUpdate, self).form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super(SubjectUpdate, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:update_subject", args = (), kwargs = {'pk': self.object.id})

		return context

	def get_success_url(self):
		return reverse_lazy('mural:render_post', args = (self.object.id, 'update', 'sub', ))

class SubjectDelete(LoginRequiredMixin, generic.DeleteView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/delete.html'
	model = SubjectPost

	def get_context_data(self, *args, **kwargs):
		context = super(SubjectDelete, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:delete_subject", args = (), kwargs = {'pk': self.object.id})
		context['message'] = _('Are you sure you want to delete this post?')

		return context

	def get_success_url(self):
		users = getSpaceUsers(self.request.user.id, self.object)
		
		paths = [reverse("mural:manage_subject")]

		notification = {
			"type": "mural",
			"subtype": "mural_delete",
			"paths": paths,
			"container": "#post-" + str(self.object.id),
		}

		notification = json.dumps(notification)

		for user in users:
			Group("user-%s" % user.id).send({'text': notification})

		return reverse_lazy('mural:deleted_post')

"""
	Section for common post functions
"""
def render_post(request, post, msg, ptype):
	if ptype == 'gen':
		post = get_object_or_404(GeneralPost, id = post)
	elif ptype == 'cat':
		post = get_object_or_404(CategoryPost, id = post)
	elif ptype == 'sub':
		post = get_object_or_404(SubjectPost, id = post)

	context = {}
	context['post'] = post

	message = ""

	if msg == 'create':
		message = _('Your post was published successfully!')
	else:
		message = _('Your post was edited successfully!')

	html = render_to_string("mural/_view.html", context, request)

	return JsonResponse({'message': message, 'view': html, 'new_id': post.id})

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

"""
	Section for comment functions
"""
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

		users = getSpaceUsers(self.request.user.id, post)
		entries = []

		notify_type = "mural"
		user_icon = self.object.user.image_url
		_view = render_to_string("mural/_view_comment.html", {"comment": self.object}, self.request)
		simple_notify = _("%s has commented in a post")%(str(self.object.user))
		pathname = reverse("mural:manage_general")

		for user in users:
			entries.append(MuralVisualizations(viewed = False, user = user, comment = self.object))
			Group("user-%s" % user.id).send({'text': json.dumps({"type": notify_type, "subtype": "create_comment", "user_icon": user_icon, "pathname": pathname, "simple": simple_notify, "complete": _view, "post_id": post.get_id()})})

		MuralVisualizations.objects.bulk_create(entries)

		return super(CommentCreate, self).form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super(CommentCreate, self).get_context_data(*args, **kwargs)

		post_id = self.kwargs.get('post', '')

		context['form_url'] = reverse_lazy("mural:create_comment", kwargs = {"post": post_id})

		return context

	def get_success_url(self):
		return reverse_lazy('mural:render_comment', args = (self.object.id, 'create', ))

class CommentUpdate(LoginRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/_form_comment.html'
	model = Comment
	form_class = CommentForm

	def form_invalid(self, form):
		context = super(CommentUpdate, self).form_invalid(form)
		context.status_code = 400

		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)

		self.object.edited = True

		self.object.save()

		users = getSpaceUsers(self.request.user.id, self.object.post)
		
		paths = [
			reverse("mural:manage_general"),
			reverse("mural:manage_category"),
			reverse("mural:manage_subject")
		]

		notification = {
			"type": "mural",
			"subtype": "mural_update",
			"paths": paths,
			"complete": render_to_string("mural/_view_comment.html", {"comment": self.object}, self.request),
			"container": "#comment-" + str(self.object.id),
		}

		notification = json.dumps(notification)

		for user in users:
			Group("user-%s" % user.id).send({'text': notification})
		
		return super(CommentUpdate, self).form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super(CommentUpdate, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:update_comment", args = (), kwargs = {'pk': self.object.id})

		return context

	def get_success_url(self):
		return reverse_lazy('mural:render_comment', args = (self.object.id, 'update', ))

class CommentDelete(LoginRequiredMixin, generic.DeleteView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mural/delete.html'
	model = Comment

	def get_context_data(self, *args, **kwargs):
		context = super(CommentDelete, self).get_context_data(*args, **kwargs)

		context['form_url'] = reverse_lazy("mural:delete_comment", args = (), kwargs = {'pk': self.object.id})
		context['message'] = _('Are you sure you want to delete this comment?')

		return context

	def get_success_url(self):
		users = getSpaceUsers(self.request.user.id, self.object.post)

		paths = [
			reverse("mural:manage_general"),
			reverse("mural:manage_category"),
			reverse("mural:manage_subject")
		]

		notification = {
			"type": "mural",
			"subtype": "mural_delete",
			"paths": paths,
			"container": "#comment-" + str(self.object.id),
		}

		notification = json.dumps(notification)

		for user in users:
			Group("user-%s" % user.id).send({'text': notification})

		return reverse_lazy('mural:deleted_comment')

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

def deleted_comment(request):
	return JsonResponse({'msg': _('Comment deleted successfully!')})

def suggest_users(request):
	param = request.GET.get('param', '')

	users = User.objects.filter(Q(username__icontains = param) | Q(last_name__icontains = param) | Q(social_name__icontains = param)).exclude(id = request.user.id)[:5]

	context = {}
	context['users'] = users

	response = render_to_string("mural/_user_suggestions_list.html", context, request)

	return JsonResponse({"search_result": response})

def load_comments(request, post, child_id):
	context = {
		'request': request,
	}

	showing = request.GET.get('showing', '')

	if showing == '':
		comments = Comment.objects.filter(post__id = post).order_by('-last_update')
	else:
		showing = showing.split(',')
		comments = Comment.objects.filter(post__id = post).exclude(id__in = showing).order_by('-last_update')	

	paginator = Paginator(comments, 5)

	try:
		page_number = int(request.GET.get('page', 1))
	except ValueError:
		raise Http404

	try:
		page_obj = paginator.page(page_number)
	except EmptyPage:
		raise Http404

	context['paginator'] = paginator
	context['page_obj'] = page_obj

	context['comments'] = page_obj.object_list
	context['post_id'] = child_id

	response = render_to_string("mural/_list_view_comment.html", context, request)

	return JsonResponse({"loaded": response})