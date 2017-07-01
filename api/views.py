import requests, json
from django.shortcuts import get_object_or_404, reverse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from security.models import Security

from subjects.serializers import SubjectSerializer
from subjects.models import Subject

from users.serializers import UserSerializer
from users.models import User

from oauth2_provider.views.generic import ProtectedResourceView
from oauth2_provider.models import Application
from django.http import HttpResponse

@csrf_exempt
def getToken(request):
	oauth = Application.objects.filter(name = "amadeus-droid")
	security = Security.objects.get(id = 1)

	response = ""

	if request.method == "POST":
		json_data = json.loads(request.body.decode('utf-8'))

		try:
			username = json_data['email']
			password = json_data['password']

			user = authenticate(username = username, password = password)

			if user is not None:
				if not security.maintence or user.is_staff:
					if oauth.count() > 0:
						oauth = oauth[0]

						data = {
							"grant_type": "password",
							"username": username,
							"password": password
						}

						auth = (oauth.client_id, oauth.client_secret)

						response = requests.post(request.build_absolute_uri(reverse('oauth2_provider:token')), data = data, auth = auth)

						json_r = json.loads(response.content.decode('utf-8'))

						json_r["message"] = ""
						json_r["type"] = ""
						json_r["title"] = ""
						json_r["success"] = True
						json_r["number"] = 1
						json_r['extra'] = 0

						response = json.dumps(json_r)
		except KeyError:
			response = "Error"
		
	return HttpResponse(response)

class LoginViewset(viewsets.ReadOnlyModelViewSet):
	queryset = User.objects.all()
	permissions_classes = (IsAuthenticated,)

	@csrf_exempt
	@list_route(methods = ['POST'], permissions_classes = [IsAuthenticated])
	def login(self, request):
		username = request.data['email']
		
		user = self.queryset.get(email = username)
		response = ""

		if not user is None:
			serializer = UserSerializer(user)

			json_r = json.dumps(serializer.data)
			json_r = json.loads(json_r)
			
			user_info = {}
			user_info["data"] = json_r

			user_info["message"] = ""
			user_info["type"] = ""
			user_info["title"] = ""
			user_info["success"] = True
			user_info["number"] = 1
			user_info['extra'] = 0

			response = json.dumps(user_info)
					
		return HttpResponse(response)

class SubjectViewset(viewsets.ReadOnlyModelViewSet):
	queryset = Subject.objects.all()
	permissions_classes = (IsAuthenticated, )

	@csrf_exempt
	@list_route(methods = ['POST'], permissions_classes = [IsAuthenticated])
	def get_subjects(self, request):
		username = request.data['email']

		user = User.objects.get(email = username)

		subjects = None

		response = ""

		if not user is None:
			if user.is_staff:
				subjects = Subject.objects.all().order_by("name")
			else:
				pk = user.pk

				subjects = Subject.objects.filter(Q(students__pk=pk) | Q(professor__pk=pk) | Q(category__coordinators__pk=pk)).distinct()

			serializer = SubjectSerializer(subjects, many = True)

			json_r = json.dumps(serializer.data)
			json_r = json.loads(json_r)
			
			sub_info = {}

			sub_info["data"] = {}
			sub_info["data"]["subjects"] = json_r

			sub_info["message"] = ""
			sub_info["type"] = ""
			sub_info["title"] = ""
			sub_info["success"] = True
			sub_info["number"] = 1
			sub_info['extra'] = 0

			response = json.dumps(sub_info)

		return HttpResponse(response)