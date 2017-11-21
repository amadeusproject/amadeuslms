""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.core.urlresolvers import reverse_lazy, reverse
from amadeus import settings
from django.contrib import messages
from os.path import join
import django.views.generic as generic
from mural.models import SubjectPost, Comment, MuralVisualizations
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, date, timedelta
from subjects.models import Subject, Tag
from .forms import CreateInteractionReportForm, ResourceAndTagForm, BaseResourceAndTagFormset
from log.models import Log
from topics.models import Resource, Topic
from collections import OrderedDict
from django.forms import formset_factory
from .models import ReportCSV, ReportXLS
import pandas as pd
import math
from io import BytesIO
import os
import copy
from django.shortcuts import render, get_object_or_404, redirect

from chat.models import Conversation, TalkMessages


from amadeus.permissions import has_category_permissions, has_subject_permissions

class ReportView(LoginRequiredMixin, generic.FormView):
    template_name = "reports/create.html"
    form_class = CreateInteractionReportForm
    

    def dispatch(self, request, *args, **kwargs):
        params = self.request.GET
        subject = Subject.objects.get(id=params['subject_id'])
       
        if not has_subject_permissions(request.user, subject):
            return redirect(reverse('subjects:home'))

        

        return super(ReportView, self).dispatch(request, *args, **kwargs)

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

        context['title'] = _('Interaction Data')
        context['subject'] = subject   

        #set formset
        resourceTagFormSet = formset_factory(ResourceAndTagForm, formset=BaseResourceAndTagFormset)
        resourceTagFormSet = resourceTagFormSet()
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

        return reverse('subjects:reports:view_report', kwargs={}) + get_params

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form = self.get_form()

        subject = Subject.objects.get(id=self.request.GET['subject_id'])

        topics = subject.topic_subject.all()
        #get all resources associated with topics
        tags = []
        for topic in topics:
            resources_set = topic.resource_topic.all()
            for resource in resources_set:
                for tag in resource.tags.all():
                    tags.append(tag)


        t = Tag(name=" ")
        t.id = -1 #so I know he choose empyt one
        tags.append(t)
        classes = Resource.__subclasses__()  
        amount_of_forms = self.request.POST['form-TOTAL_FORMS']
        initial_datum = {'class_name': classes , 'tag': tags}
        initial_data = []
        for i in range(int(amount_of_forms)):
            initial_data.append(initial_datum)

        resourceTagFormSet = formset_factory(ResourceAndTagForm, formset=BaseResourceAndTagFormset)
        resources_formset = resourceTagFormSet(self.request.POST, initial = initial_data)
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

        context['title'] = _('Interaction Data')
        context['subject_name'] = subject.name

        if params_data['topic'] == _("All"):
            context['topic_name'] = params_data['topic']
        else:
            context['topic_name'] = Topic.objects.get(id=int(params_data['topic'])).name
        context['init_date'] = params_data['init_date']
        context['end_date'] = params_data['end_date']
        context['subject'] = subject

        
        #I used getlist method so it can get more than one tag and one resource class_name
        resources = params_data.getlist('resource')
        tags = params_data.getlist('tag')
        
        self.from_mural = params_data['from_mural']
        self.from_messages = params_data['from_messages']

        context['data'], context['header'] = self.get_mural_data(subject, params_data['topic'], params_data['init_date'], params_data['end_date'],
            resources, tags )                 


        #this is to save the csv for further download
        df = pd.DataFrame.from_dict(context['data'], orient='index')
        df.columns = context['header']
        #so it does not exist more than one report CSV available for that user to download
        if ReportCSV.objects.filter(user= self.request.user).count() > 0:
            report = ReportCSV.objects.get(user=self.request.user)
            report.delete()
      
        
        report = ReportCSV(user= self.request.user, csv_data = df.to_csv())
        report.save()

        #for excel files
        if ReportXLS.objects.filter(user= self.request.user).count() > 0:
            report = ReportXLS.objects.get(user=self.request.user)
            report.delete()
        
        folder_path = join(settings.MEDIA_ROOT, 'files')
        #check if the folder already exists
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
        path = join(settings.MEDIA_ROOT, 'files' , 'report'+str(self.request.user.id)+'.xls')
        writer = pd.ExcelWriter(path)
        df.to_excel(writer, sheet_name='first_sheet')
        writer.save()
        report = ReportXLS(user= self.request.user )
        report.xls_data.name = path 
        report.save()

        return context

  
    def get_mural_data(self, subject, topics_query, init_date, end_date, resources_type_names, tags_id):
        """

            Process all the data to be brough by the report
            Subject: subject where the report is being created
            topics_query: it's either one of the topics or all of them
            init_date: When the reports filter of dates stars
            end_date: When the reports filter of dates end
            resources_type_names: resources subclasses name that were selected
            tags_id = ID of tag objects that were selected
        """
        data = {}
        students = subject.students.all()
        formats = ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"] #so it accepts english and portuguese date formats
        for fmt in formats:
            try:
                init_date = datetime.strptime(init_date, fmt).date()
                end_date = datetime.strptime(end_date, fmt).date()
                
            except ValueError:
                pass
        if topics_query == _("All"):
            topics = subject.topic_subject.all()
        else:
            topics = Topic.objects.get(id=topics_query)
        header = [str(_('User'))]
       
        #I use this so the system can gather data up to end_date 11h59 p.m.
        end_date = end_date + timedelta(days=1)
   
        self.used_tags = copy.deepcopy(tags_id) #so I can check whether we are dealing with multiple or single tags (empty option)
        #For each student in the subject
        for student in students:
            data[student.id] = []

            data[student.id].append(student.social_name)

            interactions = OrderedDict()


            

            #interactions['username'] = student.social_name
            if self.from_mural == "True":
                help_posts_made_by_user = SubjectPost.objects.filter(action="help",space__id=subject.id, user=student, 
                    create_date__range=(init_date, end_date))

                #number of help posts created by the student
                interactions[_('Number of help posts created by the user.')] = help_posts_made_by_user.count()

                help_posts = SubjectPost.objects.filter(action="help", create_date__range=(init_date, end_date), 
                space__id=subject.id)

                #comments count on help posts created by the student
                interactions[_('Amount of comments on help posts created by the student.')] = Comment.objects.filter(post__in = help_posts.filter(user=student), 
                    create_date__range=(init_date, end_date)).count()
                

                #count the amount of comments made by the student on posts made by one of the professors
                interactions[_('Amount of comments made by the student on teachers help posts.')] = Comment.objects.filter(post__in = help_posts.filter(user__in= subject.professor.all()), create_date__range=(init_date, end_date),
                 user=student).count()

                 #comments made by the user on other users posts
                interactions[_('Amount of comments made by the student on other students help posts.')] = Comment.objects.filter(post__in = help_posts.exclude(user=student), 
                    create_date__range=(init_date, end_date),
                    user= student).count()
               
                
                
                comments_by_teacher = Comment.objects.filter(user__in=subject.professor.all())
                help_posts_ids = []
                for comment in  comments_by_teacher:
                    help_posts_ids.append(comment.post.id)
                 #number of help posts created by the user that the teacher commented on
                interactions[_('Number of help posts created by the user that the teacher commented on.')] = help_posts.filter(user=student, id__in = help_posts_ids).count()

               
                comments_by_others = Comment.objects.filter(user__in=subject.students.exclude(id = student.id))
                help_posts_ids = []
                for comment in  comments_by_teacher:
                    help_posts_ids.append(comment.post.id)
                #number of help posts created by the user others students commented on
                interactions[_('Number of help posts created by the user others students commented on.')] = help_posts.filter(user=student, id__in = help_posts_ids).count()

                #Number of student visualizations on the mural of the subject
                interactions[_('Number of student visualizations on the mural of the subject.')] = MuralVisualizations.objects.filter(post__in = SubjectPost.objects.filter(space__id=subject.id, create_date__range=(init_date, end_date)),
                    user = student).count()
            

            #variables from messages
          
          
            if self.from_messages == "True":
              
                message_data = self.get_messages_data(subject, student)
                for key, value in message_data.items():
                    interactions[key] = value

            #VAR08 through VAR_019 of documenttation:
            if len(resources_type_names) > 0:
                resources_data = self.get_resources_and_tags_data(resources_type_names, tags_id, student, subject, topics, init_date, end_date)
                for key, value in resources_data.items():
                    interactions[key] = value


            #VAR20 - number of access to mural between 6 a.m to 12a.m.
            interactions[_('Number of access to mural between 6 a.m to 12a.m. .')] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (5, 11),  datetime__range=(init_date,end_date)).count()

            #VAR21 - number of access to mural between 0 p.m to 6p.m.
            interactions[_('Number of access to mural between 0 p.m to 6p.m. .')] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (11, 17), datetime__range=(init_date,end_date)).count()
            #VAR22
            interactions[_('Number of access to mural between 6 p.m to 12p.m. .')] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (17, 23),  datetime__range=(init_date,end_date)).count()

            #VAR23
            interactions[_('Number of access to mural between 0 a.m to 6a.m. .')] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__hour__range = (23, 5),  datetime__range=(init_date,end_date)).count()

            #VAR24 through 30
            day_numbers = [0, 1, 2, 3, 4, 5, 6]
            day_names = [str(_("sunday")), str(_("monday")), str(_("tuesday")), str(_("wednesday")), str(_("thursday")), 
            str(_("friday")), str(_("saturday"))]
            distinct_days = 0
            for day_num in day_numbers:
                #day+1 is because the days are started on 1 instead of the lists, which index starts at 0
                interactions[_('Number of access to the subject on ')+ day_names[day_num]] =  Log.objects.filter(action="access", resource="subject", 
                user_id= student.id, context__contains = {'subject_id' : subject.id}, datetime__week_day = day_num+1, datetime__range = (init_date, end_date)).count()
                #to save the distinct days the user has accessed 
                if interactions[_('Number of access to the subject on ')+ day_names[day_num]] > 0:
                    distinct_days += 1

            interactions[_('Number of distinct days the user access the subject. ')] = distinct_days
            interactions[_("Class")] = _("Undefined")
            interactions[_("Performance")] = _("Undefined")
            for value in interactions.values():
                data[student.id].append(value)
           
                
        for key in interactions.keys():
            header.append(key)
        return data, header

    def get_resources_and_tags_data(self, resources_types, tags, student, subject, topics, init_date, end_date):
        data = OrderedDict()  
        
        new_tags = [] #tags will be replaced by this variable
        for i in range(len(resources_types)):
           
            if tags[i] == "-1": #it means I should select all of tags available for this kind of resource
                new_tags = set()
                if not isinstance(topics,Topic):
                    topics = subject.topic_subject.all()
                    for topic in topics:
                        resource_set = Resource.objects.select_related(resources_types[i].lower()).filter(topic = topic)
                       
                        for resource in resource_set:
                            if resource._my_subclass == resources_types[i].lower():
                                for tag in resource.tags.all():
                                    if tag.name != "":
                                        new_tags.add(tag)
                else:
                    topics = topics
                    resource_set = Resource.objects.select_related(resources_types[i].lower()).filter(topic = topics)
                       
                    for resource in resource_set:
                        if resource._my_subclass == resources_types[i].lower():
                            for tag in resource.tags.all():
                                if tag.name != "":
                                    new_tags.add(tag)
                data = {}
                
              
                new_tags = [tag.id for tag in new_tags]
                tags[i] = new_tags
        for i in range(len(resources_types)):
            original_tags = copy.deepcopy(self.used_tags) #effectiving copy
            if isinstance(topics,Topic):
                if type(tags[i]) == type(list()):
                    resources = Resource.objects.select_related(resources_types[i].lower()).filter(tags__in = tags[i], topic=topics)
                else:
                    resources = Resource.objects.select_related(resources_types[i].lower()).filter(tags__in = [tags[i]], topic=topics)
            else: 
                if type(tags[i]) == type(list()):
                    resources = Resource.objects.select_related(resources_types[i].lower()).filter(tags__in = tags[i], topic__in=topics)
                else:
                    resources = Resource.objects.select_related(resources_types[i].lower()).filter(tags__in = [tags[i]], topic__in=topics)
            distinct_resources = 0
            total_count = 0
            
            #variables to handle distinct days report's variable
            day_numbers = [0, 1, 2, 3, 4, 5, 6]
            distinct_days = 0

            hours_viewed = 0 #youtube video as well as webconference
            for resource in resources:

                if isinstance(topics,Topic):
                    #if it selected only one topic to work with
                    count = Log.objects.filter(action="view", resource=resources_types[i].lower(),
                          user_id = student.id, context__contains = {'subject_id': subject.id, 
                          resources_types[i].lower()+'_id': resource.id, 'topic_id': topics.id}, datetime__range=(init_date, end_date)).count()
                    

                    if resources_types[i].lower() == "ytvideo":
                        watch_times = Log.objects.filter(action="watch", resource=resources_types[i].lower(),user_id = student.id, context__contains = {'subject_id': subject.id, 
                            resources_types[i].lower()+'_id': resource.id}, datetime__range=(init_date, end_date))
                        if watch_times.count() > 0:
                            for watch_time in watch_times:
                                begin_time = timedelta(microseconds = int(watch_time.context['timestamp_start']))
                                end_time = timedelta(microseconds =  int(watch_time.context['timestamp_end']))
                                time_delta = end_time - begin_time
                                hours_viewed +=  time_delta.microseconds/3600 #so it's turned this seconds into hours

                    if resources_types[i].lower() == "webconference":
                        init_times = Log.objects.filter(action="initwebconference", resource=resources_types[i].lower(), user_id = student.id, context__contains = {'subject_id': subject.id, 
                            resources_types[i].lower()+'_id': resource.id}, datetime__range=(init_date, end_date))
                        end_times = Log.objects.filter(action="participate", resource=resources_types[i].lower(), user_id = student.id, context__contains = {'subject_id': subject.id, 
                            resources_types[i].lower()+'_id': resource.id}, datetime__range=(init_date, end_date))
                        if init_times.count() > 0:
                            j = 0
                            for init_time in init_times:
                                begin_time = int(init_time.context['webconference_init'])
                                end_time =  int(end_times[j].context['webconference_finish'])
                                j += 1
                                time_delta = math.fabs(end_time - begin_time)
                              
                                hours_viewed +=  time_delta/3600 #so it's turned this seconds into hours
                    for day_num in day_numbers:
                        count_temp = Log.objects.filter(action="view", resource=resources_types[i].lower(),
                              user_id = student.id, context__contains = {'subject_id': subject.id, 
                              resources_types[i].lower()+'_id': resource.id, 'topic_id': topics.id}, datetime__week_day = day_num+1, datetime__range=(init_date, end_date)).count()
                        if count_temp > 0:
                            distinct_days += 1
                else:
                    #or the user selected all

                    count = Log.objects.filter(action="view", resource=resources_types[i].lower(),
                          user_id = student.id, context__contains = {'subject_id': subject.id, 
                          resources_types[i].lower()+'_id': resource.id}, datetime__range=(init_date, end_date)).count()
                   

                    for daynum in day_numbers:
                        count_temp =  Log.objects.filter(action="view", resource=resources_types[i].lower(),
                          user_id = student.id, context__contains = {'subject_id': subject.id, 
                          resources_types[i].lower()+'_id': resource.id}, datetime__week_day = daynum+1,
                           datetime__range=(init_date, end_date)).count()
                        if count_temp > 0:
                            distinct_days += 1

                    if resources_types[i].lower() == "ytvideo":
                        watch_times = Log.objects.filter(action="watch", resource=resources_types[i].lower(),user_id = student.id, context__contains = {'subject_id': subject.id, 
                            resources_types[i].lower()+'_id': resource.id}, datetime__range=(init_date, end_date))
                        if watch_times.count() > 0:
                            for watch_time in watch_times:
                                begin_time = timedelta(microseconds = int(watch_time.context['timestamp_start']))
                                end_time = timedelta(microseconds =  int(watch_time.context['timestamp_end']))
                                time_delta = end_time - begin_time
                                hours_viewed +=  time_delta.microseconds/3600 #so it's turned this seconds into hours

                    if resources_types[i].lower() == "webconference":
                        init_times = Log.objects.filter(action="initwebconference", resource=resources_types[i].lower(), user_id = student.id, context__contains = {'subject_id': subject.id, 
                            resources_types[i].lower()+'_id': resource.id}, datetime__range=(init_date, end_date))
                        end_times = Log.objects.filter(action="participate", resource=resources_types[i].lower(), user_id = student.id, context__contains = {'subject_id': subject.id, 
                            resources_types[i].lower()+'_id': resource.id}, datetime__range=(init_date, end_date))
                        if init_times.count() > 0:
                            j = 0
                            for init_time in init_times:
                                begin_time = int(init_time.context['webconference_init'])
                                end_time =  int(end_times[j].context['webconference_finish'])
                                j += 1
                                time_delta = math.fabs(end_time - begin_time)
                              
                                hours_viewed +=  time_delta/3600 #so it's turned this seconds into hours


                if count > 0:
                    distinct_resources += 1
                    total_count += count


            
            #mapping to translate class names
            mapping = {}
            mapping['pdffile'] = str(_('PDF File'))
            mapping['goals'] = str(_('Topic Goals'))
            mapping['link'] = str(_('Link to Website'))
            mapping['filelink'] = str(_('File Link'))
            mapping['webconference'] = str(_('Web Conference'))
            mapping['ytvideo'] = str(_('YouTube Video'))
            mapping['webpage'] = str(_('WebPage'))
            if original_tags[i] != "-1":
                data[str(_("number of visualizations of ")) + mapping[str(resources_types[i])] + str(_(" with tag ")) + Tag.objects.get(id=int(tags[i])).name] = total_count
                data[str(_("number of visualizations of distintic ")) +  mapping[str(resources_types[i])] + str(_(" with tag ")) + Tag.objects.get(id=int(tags[i])).name] = distinct_resources
                data[str(_("distintic days ")) +  mapping[str(resources_types[i])] + str(_(" with tag ")) + Tag.objects.get(id=int(tags[i])).name]  = distinct_days
                
                if resources_types[i].lower() in ["ytvideo", "webconference"]:
                    data[str(_("hours viewed of ")) + str(resources_types[i]) + str(_(" with tag ")) + Tag.objects.get(id=int(tags[i])).name] = hours_viewed
            else:
                data[str(_("number of visualizations of ")) + mapping[str(resources_types[i])] ] = total_count
                data[str(_("number of visualizations of distintic ")) +  mapping[str(resources_types[i])] ] = distinct_resources
                data[str(_("distintic days ")) +  mapping[str(resources_types[i])]]  = distinct_days
                
                if resources_types[i].lower() in ["ytvideo", "webconference"]:
                    data[str(_("hours viewed of ")) + str(resources_types[i]) ] = hours_viewed

        return data

    def get_messages_data(self, subject, student):
        data = OrderedDict()
        
   

        messages_sent_to_other_students = 0

        distinct_students = 0
     
        for other_student in subject.students.exclude(id = student.id):
            conversations_with_other = Conversation.objects.filter(Q(user_one=student) & Q(user_two = other_student) | Q(user_one = other_student) & Q(user_two = student) )
            messages_sent_other = TalkMessages.objects.filter(talk__in = conversations_with_other, user = student , subject= subject)
            messages_received_other = TalkMessages.objects.filter(talk__in = conversations_with_other, user = other_student, subject = subject)
            
         
         
            if data.get(_(" amount of messages sent to other students")):
                data[_(" amount of messages sent to other students")] = messages_sent_other.count() + data.get(_(" amount of messages sent to other students"))
            else:
                data[_(" amount of messages sent to other students")] = messages_sent_other.count()
           
            if data.get(_("amount of messages received from other students")):
                data[_("amount of messages received from other students")] = messages_received_other.count() + data.get(_("amount of messages received from other students"))
            else:

                data[_("amount of messages received from other students")] = messages_received_other.count()

            #check whether the other started a conversation or not
            if messages_sent_other.count() >0:
                distinct_students += 1
        
        data[_("amount of distinct students to whom sent messages")] = distinct_students
        #calculate the amount of messages sent to and received from professor
        messages_sent_professors = 0
        messages_received_professors = 0
        for professor in subject.professor.all():
            conversations_with_professor = Conversation.objects.filter(Q(user_one = student) & Q(user_two = professor) | Q(user_one = professor) & Q(user_two = student))
            messages_sent_to_professors = TalkMessages.objects.filter(talk__in = conversations_with_professor, user = student, subject = subject)

            messages_received_from_professors = TalkMessages.objects.filter(talk__in = conversations_with_professor, user = professor, subject = subject)
            if data.get(_("amount messages sent to professors")):
                data[_("amount messages sent to professors")] = messages_sent_to_professors.count() + data.get(_("amount messages sent to professors"))
            else:
                data[_("amount messages sent to professors")] = messages_sent_to_professors.count()

            if data.get(_("amount of messages received from professors")):
                data[_("amount of messages received from professors")] = messages_received_from_professors.count() + data.get(_("amount of messages received from professors"))  
            else:
                data[_("amount of messages received from professors")] = messages_received_from_professors.count() 
                     

        return data


"""
Get all possible resource subclasses available for that topic selected
"""
def get_resources(request):

    #get all possible resources 
    subject = Subject.objects.get(id=request.GET['subject_id'])

    topic_choice = request.GET["topic_choice"]
    if topic_choice.lower() == "all" or topic_choice.lower() == "todos":
        topics = subject.topic_subject.all()
    else:
        topics = [Topic.objects.get(id=int(topic_choice))]

    resources_class_names = []
    for topic in topics:
        resource_set = Resource.objects.filter(topic = topic)
        for resource in resource_set:
            resources_class_names.append(resource._my_subclass)

    #remove duplicates
    resources = set(resources_class_names)
    mapping = {}
    mapping['pdffile'] = str(_('PDF File'))
    mapping['goals'] = str(_('Topic Goals'))
    mapping['link'] = str(_('Link to Website'))
    mapping['filelink'] = str(_('File Link'))
    mapping['webconference'] = str(_('Web Conference'))
    mapping['ytvideo'] = str(_('YouTube Video'))
    mapping['webpage'] = str(_('WebPage'))
    data = {}
    data['resources']= [ {'id':resource_type, 'name':mapping[resource_type]} for resource_type in  resources]
    return JsonResponse(data)



"""
This function returns all the tags associated 
with a resource that is of the type of of the resource_class_name provided.
"""
def get_tags(request):
    resource_type = request.GET['resource_class_name']
    subject = Subject.objects.get(id=request.GET['subject_id'])
    topic_choice = request.GET["topic_choice"]
    
    #Have to fix this to accept translated options
    if topic_choice.lower() == "all" or topic_choice.lower() == "todos":
        topics = subject.topic_subject.all()
    else:
        topics = [Topic.objects.get(id=int(topic_choice))]
    data = {}
    tags = set()
    for topic in topics:
        resource_set = Resource.objects.select_related(resource_type.lower()).filter(topic = topic)
       
        for resource in resource_set:
            if resource._my_subclass == resource_type.lower():
                for tag in resource.tags.all():
                    if tag.name != "":
                        tags.add(tag)
                
   
    #adding empty tag for the purpose of giving the user this option for adicional behavior
    tags = list(tags)
    #creating empty tag
    t = Tag(name=" ")
    t.id = -1 #so I know he choose empyt one
    tags.append(t)
    data['tags'] = [ {'id':tag.id, 'name':tag.name} for tag in  tags]
    return JsonResponse(data)


def download_report_csv(request):
    report = ReportCSV.objects.get(user=request.user)
     
    response = HttpResponse(report.csv_data,content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'

    return response

def download_report_xls(request):
    report = ReportXLS.objects.get(user= request.user)

    response = HttpResponse(report.xls_data,content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="report.xls"'

    return response