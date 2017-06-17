import requests, json
from django.shortcuts import get_object_or_404, reverse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from security.models import Security

from users.serializers import UserSerializer
from users.models import User

from oauth2_provider.views.generic import ProtectedResourceView
from oauth2_provider.models import Application
from django.http import HttpResponse

class LoginViewset(viewsets.ReadOnlyModelViewSet):
	queryset = User.objects.all()
	permissions_classes = (IsAuthenticatedOrReadOnly,)

	@detail_route(methods = ['post'])
	def login(self, request):
		username = request.DATA['email']
		
		user = get_object_or_404(self.queryset, email = username)

		serializer = UserSerializer(user)
					
		return Response(serializer.data)

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
		except KeyError:
			response = "Error"
		
	return HttpResponse(response)