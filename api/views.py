import requests, json
from django.shortcuts import get_object_or_404, reverse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from security.models import Security

from users.serializers import UserSerializer
from users.models import User

from oauth2_provider.views.generic import ProtectedResourceView
from oauth2_provider.models import Application
from django.http import HttpResponse

class LoginViewset(viewsets.ReadOnlyModelViewSet):
	queryset = User.objects.all()
	permissions_classes = (IsAuthenticated,)

	@csrf_exempt
	@list_route(methods = ['POST'], permissions_classes = [IsAuthenticated])
	def login(self, request):
		username = request.data['email']
		
		user = self.queryset.get(email = username)

		if not user is None:
			serializer = UserSerializer(user)

			json_r = json.dumps(serializer.data)
			json_r = json.loads(json_r)
			print(type(serializer.data))

			json_r["message"] = ""
			json_r["type"] = ""
			json_r["title"] = ""
			json_r["success"] = True
			json_r["number"] = 1
			json_r['extra'] = 0

			response = json.dumps(json_r)
					
		return HttpResponse(response)

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