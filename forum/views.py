from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404

from .models import Forum, Post, PostAnswer
from courses.models import Topic
from core.mixins import NotificationMixin
from core.models import Action, Resource

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

class CreateForumView(LoginRequiredMixin, generic.edit.CreateView, NotificationMixin):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = 'forum/forum_form.html'
	form_class = ForumForm
	
	def form_invalid(self, form):
		context = super(CreateForumView, self).form_invalid(form)
		context.status_code = 400

		return context

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_forum', args = (self.object.id, ))
		

		action = super(CreateForumView, self).createorRetrieveAction("create Topic")
		super(CreateForumView, self).createNotification("Forum "+ self.object.name + " was created", 
			resource_name=self.object.name, resource_link= 'topics/'+self.object.slug,
			 actor=self.request.user, users = self.object.topic.subject.students.all() )
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
def load_posts(request, forum_id):
    context = {
        'request': request,
    }

    forum = get_object_or_404(Forum, id = forum_id)

    posts = Post.objects.filter(forum = forum).order_by('post_date')

    paginator = Paginator(posts, 2)
    
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

    context['posts'] = page_obj.object_list
    context['forum'] = forum

    return render(request, 'post/post_list.html', context)

class CreatePostView(LoginRequiredMixin, generic.edit.CreateView, NotificationMixin):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	form_class = PostForm

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.user = self.request.user

		self.object.save()
		super(CreatePostView, self).createNotification(self.object.user.username + " posted on " + self.object.forum,name,
		 resource_slug = self.object.forum.slug, actor=self.request.user, users= self.object.forum.topic.subject.students.all())

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
def load_answers(request, post_id):
    context = {
        'request': request,
    }

    post = get_object_or_404(Post, id = post_id)

    answers = PostAnswer.objects.filter(post = post)

    paginator = Paginator(answers, 2)
    
    try:
        page_number = int(request.GET.get('page_answer', 1))
    except ValueError:
        raise Http404

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        raise Http404

    context['paginator'] = paginator
    context['page_obj'] = page_obj

    context['answers'] = page_obj.object_list
    context['post'] = post

    return render(request, 'post_answers/post_answer_list.html', context)

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

class PostAnswerUpdateView(LoginRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	form_class = PostAnswerForm
	model = PostAnswer
	template_name = "post_answers/post_answer_form.html"
	context_object_name = 'answer'

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_post_answer', args = (self.object.id, ))
		
		return self.success_url

class PostAnswerDeleteView(LoginRequiredMixin, generic.DeleteView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	model = PostAnswer
	pk_url_kwarg = 'pk'	
	success_url = reverse_lazy('course:forum:deleted_answer')

def answer_deleted(request):
	return HttpResponse(_("Post answer deleted successfully."))