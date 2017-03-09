from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _

from django import forms

import django.views.generic as generic
from mural.models import SubjectPost, Comment, MuralVisualizations
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, date
from subjects.models import Subject
from .forms import CreateInteractionReportForm
from log.models import Log


class ReportView(LoginRequiredMixin, generic.FormView):
    template_name = "reports/report.html"
    form_class = CreateInteractionReportForm
    
    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """

        initial = {}
        params = self.request.GET
        subject = Subject.objects.get(id=params['subject_id'])
        topics = subject.topic_subject.all()
        initial['topic'] = topics
        initial['end_date'] =  date.today()
        return initial
