from django.shortcuts import render
from django.http import HttpResponse, JsonResponse


import django.views.generic as generic
from mural.models import SubjectPost
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, date
from subjects.models import Subject

class ReportView(LoginRequiredMixin, generic.TemplateView):
    template_name = "api/report.html"

    def get_context_data(self, **kwargs):
        context = {}
        params = self.request.GET
       
        if params['subject_id'] and params['init_date'] and params['end_date']:
            subject_id = params['subject_id']
            subject = Subject.objects.get(id=subject_id)
            data = {}
            students = subject.students.all()
            formats = ["%d/%m/%Y", "%m/%d/%Y"] #so it accepts english and portuguese date formats
            for fmt in formats:
                try:
                    init_date = datetime.strptime(params['init_date'], fmt)
                    end_date = datetime.strptime(params['end_date'], fmt)
                except ValueError:
                    pass

            for student in students:
                interactions = {}

                interactions['doubts'] = SubjectPost.objects.filter(action="help", create_date__range=(init_date, end_date), 
                space__id=subject_id, user=student).count()
                data[student] = interactions
              
            print(data)


        return context
