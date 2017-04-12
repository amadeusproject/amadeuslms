import datetime
from django_cron import CronJobBase, Schedule

from .utils import set_notifications

from log.models import Log
from users.models import User

class Notify(CronJobBase):
	RUN_EVERY_MINS = 1440 # every day

	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'amadeus.notification_cron'    # a unique code

	def do(self):
		set_notifications()
		
		admins = User.objects.filter(is_staff = True)
		
		if admins.count() > 0:
			admin = admins[0]

			log = Log(component = "notifications", action = "cron", resource = "notifications", user = str(admin), user_id = admin.id, user_email = admin.email, context = {})
			log.save()


def notification_cron():
	set_notifications()

	admins = User.objects.filter(is_staff = True)

	if admins.count() > 0:
		admin = admins[0]

		Log.objects.create(component = "notifications", action = "cron", resource = "notifications", user = str(admin), user_id = admin.id, user_email = admin.email, context = {})