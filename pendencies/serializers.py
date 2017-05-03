from rest_framework import serializers

from .models import Pendencies

class PendenciesSerializer(serializers.ModelSerializer):
	class Meta:
		model = Pendencies
		exclude = ('resource',)
