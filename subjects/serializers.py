from rest_framework import serializers

from .models import Tag

class TagSerializer(serializers.ModelSerializer):
	def validate(self, data):
		query = Tag.objects.filter(name = data['name'])
		
		if query.exists():
			data['id'] = query[0].id
		else:
			data['id'] = ""

		return data
	
	class Meta:
		model = Tag
		fields = '__all__'
		extra_kwargs = {
        	"name": {
	            "validators": [],
	        },
	    }
		validators = []