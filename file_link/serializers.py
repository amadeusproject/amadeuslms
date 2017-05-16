from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer
from pendencies.serializers import PendenciesSerializer
from students_group.serializers import StudentsGroupSerializer

from .models import FileLink

class SimpleFileLinkSerializer(serializers.ModelSerializer):
	topic = TopicSerializer('get_subject')
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	file_content = serializers.CharField(required = False, allow_blank = True)

	def get_subject(self, obj):
		subject = self.context.get("subject", None)

		return subject

	class Meta:
		model = FileLink
		extra_kwargs = {
        	"file_content": {
        		"required": False,
	            "validators": [],
	        },
	    }
		exclude = ('students', 'groups',)
		validators = []

class CompleteFileLinkSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	groups = StudentsGroupSerializer(many = True)

	class Meta:
		model = FileLink
		fields = '__all__'
