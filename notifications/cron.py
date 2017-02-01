import datetime
from django_cron import CronJobBase, Schedule

from .utils import set_notifications

class Notify(CronJobBase):
	RUN_EVERY_MINS = 1440 # every day

	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'amadeus.notification_cron'    # a unique code

	def do(self):
		set_notifications()

def notification_cron():
	set_notifications()