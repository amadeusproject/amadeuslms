from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Forum, Post, PostAnswer
from courses.models import Topic

from .forms import ForumForm, PostForm, PostAnswerForm

"""
	Forum Section
"""

class ForumIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = "forum/forum_list.html"
	context_object_name = 'forum'

	def get_queryset(self):
		forum_id = self.request.GET.get('forum_id', 0)

		context = Forum.objects.get(id = forum_id)
		
		return context

	def get_context_data(self, **kwargs):
		context = super(ForumIndex, self).get_context_data(**kwargs)
		context['form'] = PostForm()

		return context

class CreateForumView(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = 'forum/forum_form.html'
	form_class = ForumForm
	
	def form_invalid(self, form):
		return self.render_to_response(self.get_context_data(form = form), status = 400)

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_forum', args = (self.object.id, ))
		
		return self.success_url

def render_forum(request, forum):
	last_forum = get_object_or_404(Forum, id = forum)

	return HttpResponse(str(reverse_lazy('course:forum:view', args = (), kwargs = {'slug': last_forum.slug})) + '-' + str(forum) + '-' + str(last_forum.name))

class UpdateForumView(LoginRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = 'forum/forum_form.html'
	form_class = ForumForm
	model = Forum
	
	def form_invalid(self, form):
		return self.render_to_response(self.get_context_data(form = form), status = 400)

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_edit_forum', args = (self.object.id, ))
		
		return self.success_url

def render_edit_forum(request, forum):
	last_forum = get_object_or_404(Forum, id = forum)
	context = {
		'forum': last_forum
	}

	return render(request, 'forum/render_forum.html', context)

class ForumDeleteView(LoginRequiredMixin, generic.DeleteView):
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'

	model = Forum
	pk_url_kwarg = 'pk'	
	success_url = reverse_lazy('course:forum:deleted_forum')

def forum_deleted(request):
	return HttpResponse(_("Forum deleted successfully."))

class ForumDetailView(LoginRequiredMixin, generic.DetailView):
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'

	model = Forum
	template_name = 'forum/forum_view.html'
	context_object_name = 'forum'

	def get_context_data(self, **kwargs):
		context = super(ForumDetailView, self).get_context_data(**kwargs)
		forum = get_object_or_404(Forum, slug = self.kwargs.get('slug'))

		context['form'] = PostForm()
		context['forum'] = forum
		context['title'] = forum.name

		return context

"""
	Post Section
"""

class CreatePostView(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	form_class = PostForm

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.user = self.request.user

		self.object.save()

		return super(CreatePostView, self).form_valid(form)

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_post', args = (self.object.id, ))
		
		return self.success_url

def render_post(request, post):
	last_post = get_object_or_404(Post, id = post)

	context = {}
	context['post'] = last_post

	return render(request, "post/post_render.html", context)

class PostUpdateView(LoginRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	form_class = PostForm
	model = Post
	template_name = "post/post_update_form.html"

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_post', args = (self.object.id, ))
		
		return self.success_url

class PostDeleteView(LoginRequiredMixin, generic.DeleteView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	model = Post
	pk_url_kwarg = 'pk'	
	success_url = reverse_lazy('course:forum:deleted_post')

def post_deleted(request):
	return HttpResponse(_("Post deleted successfully."))



"""
	Post Answer Section
"""

class PostAnswerIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = "post_answers/post_answer_list.html"
	context_object_name = 'answers'

	def get_queryset(self):
		post = get_object_or_404(Post, id = self.request.GET.get('post', ''))

		context = PostAnswer.objects.filter(post = post)

		return context

class CreatePostAnswerView(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = 'post_answers/post_answer_form.html'
	form_class = PostAnswerForm

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.user = self.request.user

		self.object.save()

		return super(CreatePostAnswerView, self).form_valid(form)

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_post_answer', args = (self.object.id, ))
		
		return self.success_url

def render_post_answer(request, answer):
	last_answer = get_object_or_404(PostAnswer, id = answer)

	context = {}
	context['answer'] = last_answer

	return render(request, "post_answers/post_answer_render.html", context)