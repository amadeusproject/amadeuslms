import json
import textwrap
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _

from fcm_django.models import FCMDevice
from fcm_django.fcm import fcm_send_message

from chat.serializers import ChatSerializer

def  sendChatPushNotification(user, message):
	device = FCMDevice.objects.filter(user = user, active = True).first()

	if not device is None:
		serializer = ChatSerializer(message)

		json_r = json.dumps(serializer.data)
		json_r = json.loads(json_r)
		
		info = {}

		info["data"] = {}
		info["data"]["messages"] = []
		info["data"]["message_sent"] = json_r

		info["message"] = ""
		info["type"] = ""
		info["title"] = ""
		info["success"] = True
		info["number"] = 1
		info['extra'] = 0

		response = json.dumps(info)

		title = str(user).join(_(" sent a message"))

		simple_notify = textwrap.shorten(strip_tags(message.text), width = 30, placeholder = "...")

		if message.image:
			simple_notify += " ".join(_("[Photo]"))

		device.send_message(title = title, body = simple_notify, data = {"response": response})