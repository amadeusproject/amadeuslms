from django.shortcuts import render
#API IMPORTS
from rest_framework import viewsets
from .serializers import LogSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Log
# Create your views here.

#REST API VIEWS
class LogViewSet(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]
	queryset = Log.objects.all()
	serializer_class = LogSerializer