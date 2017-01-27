import datetime
from django_cron import CronJobBase, Schedule

from .utils import set_notifications

class Notify(CronJobBase):
	RUN_EVERY_MINS = 1 # every minute

	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'amadeus.notification_cron'    # a unique code

	def do(self):
		print("Hey")
		set_notifications()