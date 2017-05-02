from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer

from .models import PDFFile

class SimplePDFFileSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)

	class Meta:
		model = PDFFile
		exclude = ('students', 'groups',)
