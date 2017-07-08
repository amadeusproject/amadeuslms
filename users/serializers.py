import os
import zipfile
import time
from django.conf import settings
from django.core.files import File
from rest_framework import serializers

from log.serializers import LogSerializer
from log.models import Log

from .models import User

class UserBackupSerializer(serializers.ModelSerializer):
	log = LogSerializer(many = True, source = 'get_items')
	image = serializers.CharField(required = False, allow_blank = True, max_length = 255)

	def validate(self, data):
		user = User.objects.filter(email = data["email"])
		
		if user.exists():
			log = data["get_items"]
			data = user[0].__dict__
			data["get_items"] = log
		else:
			data["id"] = ""

		files = self.context.get('files', None)
		
		if files:
			if data["image"] in files.namelist(): 
				file_path = os.path.join(settings.MEDIA_ROOT, data["image"])

				if os.path.isfile(file_path):
					dst_path = os.path.join(settings.MEDIA_ROOT, "tmp")

					path = files.extract(data["image"], dst_path)

					new_name = "users/img_" + str(time.time()) + os.path.splitext(data["image"])[1]

					os.rename(os.path.join(dst_path, path), os.path.join(settings.MEDIA_ROOT, new_name))
					
					data["image"] = new_name
				else:
					path = files.extract(data["image"], settings.MEDIA_ROOT)
			else:
				data["image"] = None

		return data

	class Meta:
		model = User
		fields = '__all__'
		extra_kwargs = {
        	"email": {
	            "validators": [],
	        },
	    }
		validators = []

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username','email','image_url','last_update','date_created','last_name','social_name',
			'is_staff','is_active','description')
