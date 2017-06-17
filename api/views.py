import requests
from django.shortcuts import get_object_or_404, reverse
from django.contrib.auth import authenticate
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
	security = Security.objects.get(id = 1)
	permissions_classes = (IsAuthenticatedOrReadOnly,)

	@detail_route(methods = ['post'])
	def login(self, request):
		username = request.DATA['email']
		
		user = get_object_or_404(self.queryset, email = username)

		serializer = UserSerializer(user)
					
		return Response(serializer.data)

def getToken(request):
	oauth = Application.objects.filter(name = "amadeus-droid")

	response = ""

	if request.POST:
		username = request.POST['email']
		password = request.POST['password']

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
		
	return HttpResponse(response)