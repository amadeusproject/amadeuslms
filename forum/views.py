from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string

from rolepermissions.mixins import HasRoleMixin
from rolepermissions.verifications import has_object_permission

from .models import Forum, Post, PostAnswer
from courses.models import Topic
from core.models import Action, Resource

from .forms import ForumForm, PostForm, PostAnswerForm

from core.mixins import LogMixin, NotificationMixin

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

class CreateForumView(LoginRequiredMixin, HasRoleMixin, generic.edit.CreateView, LogMixin, NotificationMixin):
	log_component = "forum"
	log_action = "create"
	log_resource = "forum"
	log_context = {}

	allowed_roles = ['professor', 'system_admin']

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
			resource_name=self.object.name, resource_link= reverse('course:forum:view', args=[self.object.slug]),
			 actor=self.request.user, users = self.object.topic.subject.students.all() )

		self.log_context['forum_id'] = self.object.id
		self.log_context['forum_name'] = self.object.name
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['course_id'] = self.object.topic.subject.course.id
		self.log_context['course_name'] = self.object.topic.subject.course.name
		self.log_context['course_slug'] = self.object.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.topic.subject.course.category.name

		super(CreateForumView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return self.success_url

def render_forum(request, forum):
	last_forum = get_object_or_404(Forum, id = forum)

	return JsonResponse({'url': str(reverse_lazy('course:forum:view', args = (), kwargs = {'slug': last_forum.slug})), 'forum_id': str(forum), 'name': str(last_forum.name), 'message': _('Forum created successfully!')})

class UpdateForumView(LoginRequiredMixin, HasRoleMixin, generic.UpdateView, LogMixin):
	log_component = "forum"
	log_action = "update"
	log_resource = "forum"
	log_context = {}

	allowed_roles = ['professor', 'system_admin']

	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = 'forum/forum_form.html'
	form_class = ForumForm
	model = Forum
	
	def dispatch(self, *args, **kwargs):
		forum = get_object_or_404(Forum, id = self.kwargs.get('pk'))

		if(not has_object_permission('edit_forum', self.request.user, forum)):
			return self.handle_no_permission()

		return super(UpdateForumView, self).dispatch(*args, **kwargs)

	def form_invalid(self, form):
		return self.render_to_response(self.get_context_data(form = form), status = 400)

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_edit_forum', args = (self.object.id, ))

		self.log_context['forum_id'] = self.object.id
		self.log_context['forum_name'] = self.object.name
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['course_id'] = self.object.topic.subject.course.id
		self.log_context['course_name'] = self.object.topic.subject.course.name
		self.log_context['course_slug'] = self.object.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.topic.subject.course.category.name

		super(UpdateForumView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)
		
		return self.success_url

def render_edit_forum(request, forum):
	last_forum = get_object_or_404(Forum, id = forum)
	context = {
		'forum': last_forum
	}

	return render(request, 'forum/render_forum.html', context)

class ForumDeleteView(LoginRequiredMixin, HasRoleMixin, generic.DeleteView, LogMixin):
	log_component = "forum"
	log_action = "delete"
	log_resource = "forum"
	log_context = {}

	allowed_roles = ['professor', 'system_admin']

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'

	model = Forum
	pk_url_kwarg = 'pk'	

	def dispatch(self, *args, **kwargs):
		forum = get_object_or_404(Forum, id = self.kwargs.get('pk'))

		if(not has_object_permission('delete_forum', self.request.user, forum)):
			return self.handle_no_permission()

		return super(ForumDeleteView, self).dispatch(*args, **kwargs)

	def get_success_url(self):
		self.log_context['forum_id'] = self.object.id
		self.log_context['forum_name'] = self.object.name
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['course_id'] = self.object.topic.subject.course.id
		self.log_context['course_name'] = self.object.topic.subject.course.name
		self.log_context['course_slug'] = self.object.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.topic.subject.course.category.name

		super(ForumDeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('course:forum:deleted_forum')

def forum_deleted(request):
	return HttpResponse(_("Forum deleted successfully."))

class ForumDetailView(LoginRequiredMixin, LogMixin, generic.DetailView):
	log_component = "forum"
	log_action = "viewed"
	log_resource = "forum"
	log_context = {}

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'

	model = Forum
	template_name = 'forum/forum_view.html'
	context_object_name = 'forum'

	def dispatch(self, *args, **kwargs):
		forum = get_object_or_404(Forum, slug = self.kwargs.get('slug'))

		if(not has_object_permission('view_forum', self.request.user, forum)):
			return self.handle_no_permission()

		self.log_context['forum_id'] = forum.id
		self.log_context['forum_name'] = forum.name
		self.log_context['topic_id'] = forum.topic.id
		self.log_context['topic_name'] = forum.topic.name
		self.log_context['topic_slug'] = forum.topic.slug
		self.log_context['subject_id'] = forum.topic.subject.id
		self.log_context['subject_name'] = forum.topic.subject.name
		self.log_context['subject_slug'] = forum.topic.subject.slug
		self.log_context['course_id'] = forum.topic.subject.course.id
		self.log_context['course_name'] = forum.topic.subject.course.name
		self.log_context['course_slug'] = forum.topic.subject.course.slug
		self.log_context['course_category_id'] = forum.topic.subject.course.category.id
		self.log_context['course_category_name'] = forum.topic.subject.course.category.name

		super(ForumDetailView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return super(ForumDetailView, self).dispatch(*args, **kwargs)

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

    showing = request.GET.get('showing', '')

    if showing == '':
        posts = Post.objects.filter(forum = forum).order_by('post_date')
    else:
        showing = showing.split(',')
        posts = Post.objects.filter(forum = forum).exclude(id__in = showing).order_by('post_date')

    paginator = Paginator(posts, 5)
    
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

    html = render_to_string('post/post_load_more_render.html', context, request)

    return JsonResponse({'num_pages': paginator.num_pages, 'page': page_obj.number, 'btn_text': _('Load more posts'), 'html': html})

class CreatePostView(LoginRequiredMixin, generic.edit.CreateView, LogMixin, NotificationMixin):
	log_component = "forum"
	log_action = "create"
	log_resource = "post"
	log_context = {}

	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	form_class = PostForm

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.user = self.request.user

		self.object.save()
		
		super(CreatePostView, self).createNotification(" posted on " + self.object.forum.name,
		 resource_slug = self.object.forum.slug, actor=self.request.user, users= self.object.forum.topic.subject.students.all(),
		 resource_link = reverse('course:forum:view', args=[self.object.forum.slug]))

		self.log_context['post_id'] = self.object.id
		self.log_context['forum_id'] = self.object.forum.id
		self.log_context['forum_name'] = self.object.forum.name
		self.log_context['topic_id'] = self.object.forum.topic.id
		self.log_context['topic_name'] = self.object.forum.topic.name
		self.log_context['topic_slug'] = self.object.forum.topic.slug
		self.log_context['subject_id'] = self.object.forum.topic.subject.id
		self.log_context['subject_name'] = self.object.forum.topic.subject.name
		self.log_context['subject_slug'] = self.object.forum.topic.subject.slug
		self.log_context['course_id'] = self.object.forum.topic.subject.course.id
		self.log_context['course_name'] = self.object.forum.topic.subject.course.name
		self.log_context['course_slug'] = self.object.forum.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.forum.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.forum.topic.subject.course.category.name

		super(CreatePostView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return super(CreatePostView, self).form_valid(form)

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_post', args = (self.object.id, ))
		
		return self.success_url

def render_post(request, post):
	last_post = get_object_or_404(Post, id = post)

	context = {}
	context['post'] = last_post

	html = render_to_string("post/post_render.html", context, request)

	return JsonResponse({'new_id': last_post.id, 'html': html})

class PostUpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
	log_component = "forum"
	log_action = "update"
	log_resource = "post"
	log_context = {}

	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	form_class = PostForm
	model = Post
	template_name = "post/post_update_form.html"

	def form_valid(self, form):
		self.object = form.save()

		self.log_context['post_id'] = self.object.id
		self.log_context['forum_id'] = self.object.forum.id
		self.log_context['forum_name'] = self.object.forum.name
		self.log_context['topic_id'] = self.object.forum.topic.id
		self.log_context['topic_name'] = self.object.forum.topic.name
		self.log_context['topic_slug'] = self.object.forum.topic.slug
		self.log_context['subject_id'] = self.object.forum.topic.subject.id
		self.log_context['subject_name'] = self.object.forum.topic.subject.name
		self.log_context['subject_slug'] = self.object.forum.topic.subject.slug
		self.log_context['course_id'] = self.object.forum.topic.subject.course.id
		self.log_context['course_name'] = self.object.forum.topic.subject.course.name
		self.log_context['course_slug'] = self.object.forum.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.forum.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.forum.topic.subject.course.category.name

		super(PostUpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return super(PostUpdateView, self).form_valid(form)

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_post', args = (self.object.id, ))
		
		return self.success_url

class PostDeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
	log_component = "forum"
	log_action = "delete"
	log_resource = "post"
	log_context = {}

	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	model = Post
	pk_url_kwarg = 'pk'	

	def get_success_url(self):
		self.success_url = reverse_lazy('course:forum:deleted_post')

		self.log_context['post_id'] = self.object.id
		self.log_context['forum_id'] = self.object.forum.id
		self.log_context['forum_name'] = self.object.forum.name
		self.log_context['topic_id'] = self.object.forum.topic.id
		self.log_context['topic_name'] = self.object.forum.topic.name
		self.log_context['topic_slug'] = self.object.forum.topic.slug
		self.log_context['subject_id'] = self.object.forum.topic.subject.id
		self.log_context['subject_name'] = self.object.forum.topic.subject.name
		self.log_context['subject_slug'] = self.object.forum.topic.subject.slug
		self.log_context['course_id'] = self.object.forum.topic.subject.course.id
		self.log_context['course_name'] = self.object.forum.topic.subject.course.name
		self.log_context['course_slug'] = self.object.forum.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.forum.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.forum.topic.subject.course.category.name

		super(PostDeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)
		
		return self.success_url

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

    showing = request.GET.get('showing_ans', '')

    if showing == '':
        answers = PostAnswer.objects.filter(post = post)
    else:
        showing = showing.split(',')
        answers = PostAnswer.objects.filter(post = post).exclude(id__in = showing)

    paginator = Paginator(answers, 5)
    
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

    html = render_to_string('post_answers/post_answer_load_more_render.html', context, request)

    return JsonResponse({'num_pages': paginator.num_pages, 'page': page_obj.number, 'btn_text': _('Load more answers'), 'html': html})

class PostAnswerIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = "post_answers/post_answer_list.html"
	context_object_name = 'answers'

	def get_queryset(self):
		post = get_object_or_404(Post, id = self.request.GET.get('post', ''))

		context = PostAnswer.objects.filter(post = post)

		return context

class CreatePostAnswerView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
	log_component = "forum"
	log_action = "create"
	log_resource = "post_answer"
	log_context = {}

	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = 'post_answers/post_answer_form.html'
	form_class = PostAnswerForm

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.user = self.request.user

		self.object.save()

		self.log_context['post_answer_id'] = self.object.id
		self.log_context['post_id'] = self.object.post.id
		self.log_context['post_user_id'] = self.object.post.user.id
		self.log_context['post_user_name'] = self.object.post.user.name
		self.log_context['forum_id'] = self.object.post.forum.id
		self.log_context['forum_name'] = self.object.post.forum.name
		self.log_context['topic_id'] = self.object.post.forum.topic.id
		self.log_context['topic_name'] = self.object.post.forum.topic.name
		self.log_context['topic_slug'] = self.object.post.forum.topic.slug
		self.log_context['subject_id'] = self.object.post.forum.topic.subject.id
		self.log_context['subject_name'] = self.object.post.forum.topic.subject.name
		self.log_context['subject_slug'] = self.object.post.forum.topic.subject.slug
		self.log_context['course_id'] = self.object.post.forum.topic.subject.course.id
		self.log_context['course_name'] = self.object.post.forum.topic.subject.course.name
		self.log_context['course_slug'] = self.object.post.forum.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.post.forum.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.post.forum.topic.subject.course.category.name

		super(CreatePostAnswerView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return super(CreatePostAnswerView, self).form_valid(form)

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_post_answer', args = (self.object.id, ))
		
		return self.success_url

def render_post_answer(request, answer):
	last_answer = get_object_or_404(PostAnswer, id = answer)

	context = {}
	context['answer'] = last_answer

	html = render_to_string("post_answers/post_answer_render.html", context, request)

	return JsonResponse({'new_id': last_answer.id, 'html': html})

class PostAnswerUpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
	log_component = "forum"
	log_action = "update"
	log_resource = "post_answer"
	log_context = {}

	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	form_class = PostAnswerForm
	model = PostAnswer
	template_name = "post_answers/post_answer_form.html"
	context_object_name = 'answer'

	def get_success_url(self):
		self.success_url = reverse('course:forum:render_post_answer', args = (self.object.id, ))

		self.log_context['post_answer_id'] = self.object.id
		self.log_context['post_id'] = self.object.post.id
		self.log_context['post_user_id'] = self.object.post.user.id
		self.log_context['post_user_name'] = self.object.post.user.name
		self.log_context['forum_id'] = self.object.post.forum.id
		self.log_context['forum_name'] = self.object.post.forum.name
		self.log_context['topic_id'] = self.object.post.forum.topic.id
		self.log_context['topic_name'] = self.object.post.forum.topic.name
		self.log_context['topic_slug'] = self.object.post.forum.topic.slug
		self.log_context['subject_id'] = self.object.post.forum.topic.subject.id
		self.log_context['subject_name'] = self.object.post.forum.topic.subject.name
		self.log_context['subject_slug'] = self.object.post.forum.topic.subject.slug
		self.log_context['course_id'] = self.object.post.forum.topic.subject.course.id
		self.log_context['course_name'] = self.object.post.forum.topic.subject.course.name
		self.log_context['course_slug'] = self.object.post.forum.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.post.forum.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.post.forum.topic.subject.course.category.name

		super(PostAnswerUpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)
		
		return self.success_url

class PostAnswerDeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
	log_component = "forum"
	log_action = "delete"
	log_resource = "post_answer"
	log_context = {}

	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	model = PostAnswer
	pk_url_kwarg = 'pk'

	def get_success_url(self):
		self.success_url = reverse_lazy('course:forum:deleted_answer')

		self.log_context['post_answer_id'] = self.object.id
		self.log_context['post_id'] = self.object.post.id
		self.log_context['post_user_id'] = self.object.post.user.id
		self.log_context['post_user_name'] = self.object.post.user.name
		self.log_context['forum_id'] = self.object.post.forum.id
		self.log_context['forum_name'] = self.object.post.forum.name
		self.log_context['topic_id'] = self.object.post.forum.topic.id
		self.log_context['topic_name'] = self.object.post.forum.topic.name
		self.log_context['topic_slug'] = self.object.post.forum.topic.slug
		self.log_context['subject_id'] = self.object.post.forum.topic.subject.id
		self.log_context['subject_name'] = self.object.post.forum.topic.subject.name
		self.log_context['subject_slug'] = self.object.post.forum.topic.subject.slug
		self.log_context['course_id'] = self.object.post.forum.topic.subject.course.id
		self.log_context['course_name'] = self.object.post.forum.topic.subject.course.name
		self.log_context['course_slug'] = self.object.post.forum.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.post.forum.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.post.forum.topic.subject.course.category.name

		super(PostAnswerDeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)
		
		return self.success_url

def answer_deleted(request):
	return HttpResponse(_("Post answer deleted successfully."))