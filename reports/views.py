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
from .forms import CreateInteractionReportForm, ResourceAndTagForm
from log.models import Log
from topics.models import Resource, Topic

from django.forms import formset_factory

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
        initial['subject'] = subject
        initial['topic'] = topics
        initial['end_date'] =  date.today()
        return initial

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)
        subject = Subject.objects.get(id=self.request.GET['subject_id'])

        context['subject'] = subject

        topics = subject.topic_subject.all()
        #get all resources associated with topics
        resources = []
        tags = []
        for topic in topics:
            resources_set = topic.resource_topic.all()
            for resource in resources_set:
                for tag in resource.tags.all():
                    tags.append(tag)
                resources.append(resource)
        context['resources'] = resources
        context['tags'] = tags
        

        #set formset
        resourceTagFormSet = formset_factory(ResourceAndTagForm, extra = 1)
        resourceTagFormSet = resourceTagFormSet(initial=[{'resource':resources, 'tag':tags}])
        context['resource_tag_formset'] = resourceTagFormSet
        return context

    def get_success_url(self):

        messages.success(self.request, _("Report created successfully"))

        get_params = "?"
        #passing form data through GET 
        for key, value in self.form_data.items():
            get_params += key +  "=" + str(value)  + "&"

        
        for form_data in self.formset_data:   
            for key, value in form_data.items():
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

        subject = Subject.objects.get(id=self.request.GET['subject_id'])

        topics = subject.topic_subject.all()
        #get all resources associated with topics
        resources = []
        tags = []
        for topic in topics:
            resources_set = topic.resource_topic.all()
            for resource in resources_set:
                for tag in resource.tags.all():
                    tags.append(tag)
                resources.append(resource)
        resourceTagFormSet = formset_factory(ResourceAndTagForm, extra= 1)
        resources_formset = resourceTagFormSet(self.request.POST, initial=[{'resource':resources, 'tag':tags}])
        if form.is_valid() and resources_formset.is_valid():
            self.form_data = form.cleaned_data
            self.formset_data = resources_formset.cleaned_data
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
            interactions['number of help posts created by the user'] = help_posts_made_by_user.count()

            help_posts = SubjectPost.objects.filter(action="help", create_date__range=(init_date, end_date), 
            space__id=subject.id)

            #comments count on help posts created by the student
            interactions['amount of comments on help posts created by the student'] = Comment.objects.filter(post__in = help_posts.filter(user=student), 
                create_date__range=(init_date, end_date)).count()
            

            #count the amount of comments made by the student on posts made by one of the professors
            interactions['amount of comments made by the student on teachers help posts'] = Comment.objects.filter(post__in = help_posts.filter(user__in= subject.professor.all()), create_date__range=(init_date, end_date),
             user=student).count()

             #comments made by the user on other users posts
            interactions['amount of comments made by the student on other students help posts'] = Comment.objects.filter(post__in = help_posts.exclude(user=student), 
                create_date__range=(init_date, end_date),
                user= student).count()
           
            
           
            comments_by_teacher = Comment.objects.filter(user__in=subject.professor.all())
            help_posts_ids = []
            for comment in  comments_by_teacher:
                help_posts_ids.append(comment.post.id)
             #number of help posts created by the user that the teacher commented on
            interactions['Number of help posts created by the user that the teacher commented on'] = help_posts.filter(user=student, id__in = help_posts_ids).count()

           
            comments_by_others = Comment.objects.filter(user__in=subject.students.exclude(id = student.id))
            help_posts_ids = []
            for comment in  comments_by_teacher:
                help_posts_ids.append(comment.post.id)
            #number of help posts created by the user others students commented on
            interactions['number of help posts created by the user others students commented on'] = help_posts.filter(user=student, id__in = help_posts_ids).count()

            #Number of student visualizations on the mural of the subject
            interactions['Number of student visualizations on the mural of the subject'] = MuralVisualizations.objects.filter(post__in = SubjectPost.objects.filter(space__id=subject.id),
                user = student).count()
            

            #VAR20 - number of access to mural between 6 a.m to 12a.m.
            interactions[' number of access to mural between 6 a.m to 12a.m.'] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (5, 11)).count()

            #VAR21 - number of access to mural between 0 p.m to 6p.m.
            interactions['number of access to mural between 0 p.m to 6p.m.'] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (11, 17)).count()
            #VAR22
            interactions[' number of access to mural between 6 p.m to 12p.m.'] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (17, 23)).count()

            #VAR23
            interactions[' number of access to mural between 0 a.m to 6a.m.'] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (23, 5)).count()

            #VAR24 through 30
            day_numbers = [0, 1, 2, 3, 4, 5, 6]
            day_names = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
            for day_num in day_numbers:
                interactions['number of access to the subject on '+ day_names[day_num]] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__week_day = day_num).count()
             
            for value in interactions.values():
                data[student].append(value)
            if len(header) <= 1:
                for key in interactions.keys():
                    header.append(key)
        return data, header



def get_resources(request):
    subject = Subject.objects.get(id=request.GET['subject_id'])

    topics = subject.topic_subject.all()
    #get all resources associated with topics
    resources = []
    tags = []
    for topic in topics:
        resources_set = topic.resource_topic.all()
        for resource in resources_set:
            for tag in resource.tags.all():
                tags.append(tag)
            resources.append(resource)

    data = {}
   
    data['resources']= [ {'id':resource.id, 'name':resource.name} for resource in  resources]
    return JsonResponse(data)


def get_tags(request):
    resource = Resource.objects.get(id=request.GET['resource_id'])
    data = {}
    tags = []
   
    for tag in resource.tags.all():
        tags.append(tag)
    data['tags'] = [ {'id':tag.id, 'name':tag.name} for tag in  tags]
    return JsonResponse(data)
