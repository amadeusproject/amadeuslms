from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import authenticate, login as login_user
from django.contrib.auth.mixins import LoginRequiredMixin
from .decorators import log_decorator
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.generic import CreateView, UpdateView, ListView
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail,BadHeaderError
from django.conf import settings
from core.mixins import NotificationMixin
from .models import Notification, Log
from rolepermissions.shortcuts import assign_role
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#API REST IMPORTS
from .serializers import LogSerializer
from rest_framework import status, serializers, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .forms import RegisterUserForm
from .decorators import log_decorator, notification_decorator

from users.models import User
from courses.models import Course, CourseCategory

from courses.views import course_category

def index(request):
	context = {
		'subscribed_courses': 'testando'
	}
	return render(request, "index.html", context)


class RegisterUser(CreateView, NotificationMixin):
	model = User
	form_class = RegisterUserForm
	template_name = 'register_user.html'

	success_url = reverse_lazy('core:home')

	def form_valid(self, form):
		form.save()
		assign_role(form.instance, 'student')

		messages.success(self.request, _('User successfully registered!'))

		return super(RegisterUser, self).form_valid(form)


def create_account(request):
	return render(request, "create_account.html")

def login(request):
	context = {}
	context['title'] = 'Log In'

	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			login_user(request, user)
			return redirect(reverse("app:index"))
		else:
			messages.add_message(request, messages.ERROR, _('E-mail or password are incorrect.'))
			context["username"] = username
	elif request.user.is_authenticated:
		return redirect(reverse('app:index'))

	return render(request,"index.html",context)

def processNotification(self, notificationId):
	notification = Notification.objects.get(id= notificationId)
	notification.read = True
	notification.save()
	return redirect(notification.action_resource.resource.url)

def getNotifications(request):
	context = {}
	if request.user.is_authenticated:
		amountGotten = 0 #amountOfNotifications actually received
		steps = int(request.GET['steps'])
		amount = int(request.GET['amount'])
		notifications = Notification.objects.filter(user= request.user, read=False).order_by('-datetime')[steps:steps+amount]
		if len(notifications) == 0:
			return HttpResponse("nothing")
		else:
			amountGotten = len(notifications)
		context['notifications'] = notifications
	else: #go to login page
		return HttpResponse('teste')


	html = render_to_string("notifications.html", context)
	data = {}
	data['html'] = html
	data['amountGotten'] = amountGotten
	return JsonResponse(data)


class GuestView (ListView):

	template_name = 'guest.html'
	context_object_name = 'courses'
	queryset = CourseCategory.objects.all()

	def get_context_data (self, **kwargs):
		context = super(GuestView, self).get_context_data(**kwargs)
		context['title'] = _("Guest")
		queryset_list = Course.objects.filter(public=True)

		# paginator = Paginator(queryset_list, 3)
		# page = self.request.GET.get('page')
		# try:
		# 	queryset_list = paginator.page(page)
		# except PageNotAnInteger:
		# 	queryset_list = paginator.page(1)
		# except EmptyPage:
		# 	queryset_list = paginator.page(paginator.num_pages)

		context['categorys_courses'] = course_category(queryset_list)
		return context



#REST API VIEWS
class LogViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	queryset = Log.objects.all()
	serializer_class = LogSerializer
