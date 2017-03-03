import datetime
from django_cron import CronJobBase, Schedule

from .utils import set_goals

class SetGoals(CronJobBase):
	RUN_EVERY_MINS = 1440 # every day

	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'amadeus.goals_cron'    # a unique code

	def do(self):
		set_goals()

def setgoals_cron():
	set_goals()