from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.core.urlresolvers import reverse_lazy

from django.contrib import messages

import django.views.generic as generic
from mural.models import SubjectPost, Comment, MuralVisualizations
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, date
from subjects.models import Subject
from .forms import CreateInteractionReportForm
from log.models import Log


class ReportView(LoginRequiredMixin, generic.FormView):
    template_name = "reports/create.html"
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

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)
        subject = Subject.objects.get(id=self.request.GET['subject_id'])

        context['subject'] = subject
       
        return context

    def get_success_url(self):

        messages.success(self.request, _("Report created successfully"))

        get_params = "?"
        #passing form data through GET 
        for key, value in self.form_data.items():
            get_params += key +  "=" + str(value)  + "&"

        
        #retrieving subject id for data purposes
        for key, value in self.request.GET.items():
            get_params += key + "=" + str(value) 

        return reverse_lazy('subjects:reports:view_report', kwargs={}) + get_params

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form = self.get_form()
        if form.is_valid():

            self.form_data = form.cleaned_data
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ViewReportView(LoginRequiredMixin, generic.TemplateView):
    template_name = "reports/view.html"


    def get_context_data(self, **kwargs):
        context = {}
        params_data = self.request.GET
        subject = Subject.objects.get(id=params_data['subject_id'])
        context['subject_name'] = subject.name
        context['topic_name'] = params_data['topic']
        context['init_date'] = params_data['init_date']
        context['end_date'] = params_data['end_date']
        context['subject'] = subject
        if params_data['from_mural']:
            context['data'], context['header'] = self.get_mural_data(subject, params_data['init_date'], params_data['end_date'])
        return context

    def get_mural_data(self, subject, init_date, end_date):
        data = {}
        students = subject.students.all()
        formats = ["%d/%m/%Y", "%m/%d/%Y"] #so it accepts english and portuguese date formats
        for fmt in formats:
            try:
                init_date = datetime.strptime(init_date, fmt)
                end_date = datetime.strptime(end_date, fmt)
            except ValueError:
                pass

        header = ['User']

        for student in students:
            data[student] = []

            data[student].append(student.social_name)

            interactions = {}
            #interactions['username'] = student.social_name
            
            help_posts_made_by_user = SubjectPost.objects.filter(action="help",space__id=subject.id, user=student, 
                create_date__range=(init_date, end_date))

            #number of help posts created by the student
            interactions['v01'] = help_posts_made_by_user.count()

            help_posts = SubjectPost.objects.filter(action="help", create_date__range=(init_date, end_date), 
            space__id=subject.id)

            #comments count on help posts created by the student
            interactions['v02'] = Comment.objects.filter(post__in = help_posts.filter(user=student), 
                create_date__range=(init_date, end_date)).count()
            

            #count the amount of comments made by the student on posts made by one of the professors
            interactions['v03'] = Comment.objects.filter(post__in = help_posts.filter(user__in= subject.professor.all()), create_date__range=(init_date, end_date),
             user=student).count()

             #comments made by the user on other users posts
            interactions['v04'] = Comment.objects.filter(post__in = help_posts.exclude(user=student), 
                create_date__range=(init_date, end_date),
                user= student).count()
           
            
           
            comments_by_teacher = Comment.objects.filter(user__in=subject.professor.all())
            help_posts_ids = []
            for comment in  comments_by_teacher:
                help_posts_ids.append(comment.post.id)
             #number of help posts created by the user that the teacher commented on
            interactions['v05'] = help_posts.filter(user=student, id__in = help_posts_ids).count()

           
            comments_by_others = Comment.objects.filter(user__in=subject.students.exclude(id = student.id))
            help_posts_ids = []
            for comment in  comments_by_teacher:
                help_posts_ids.append(comment.post.id)
            #number of help posts created by the user others students commented on
            interactions['v06'] = help_posts.filter(user=student, id__in = help_posts_ids).count()

            #Number of student visualizations on the mural of the subject
            interactions['v07'] = MuralVisualizations.objects.filter(post__in = SubjectPost.objects.filter(space__id=subject.id),
                user = student).count()
            

            #VAR20 - number of access to mural between 6 a.m to 12a.m.
            interactions['v20'] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (5, 11)).count()

            #VAR21 - number of access to mural between 6 a.m to 12a.m.
            interactions['v21'] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (11, 17)).count()
            #VAR22
            interactions['v22'] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (17, 23)).count()

            #VAR23
            interactions['v23'] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (23, 5)).count()

            #VAR24 through 30
            day_numbers = [0, 1, 2, 3, 4, 5, 6]
            day_names = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
            for day_num in day_numbers:
                interactions['v'+ str(24+day_num)] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__week_day = day_num).count()
             
            for value in interactions.values():
                data[student].append(value)
            if len(header) <= 1:
                for key in interactions.keys():
                    header.append(key)
        return data, header

