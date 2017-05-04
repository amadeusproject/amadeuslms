from django.shortcuts import render

# Create your views here.
from django.views import generic
from django.db.models import Count

from subjects.models import Tag, Subject
from topics.models import Resource
from users.models import User
from django.http import HttpResponse, JsonResponse


class GeneralView(generic.TemplateView):
    template_name = "analytics/general.html"

    def get_context_data(self, **kwargs):
        context = {}
        
        return context



def most_used_tags(request):
    tags = Tag.objects.all()

    data = {}
    #grab all references to that tag
    for tag in tags:
        subjects_count =  Subject.objects.filter(tags = tag).count()
        if  subjects_count > 0:
            data[tag.name] = {'name': tag.name}
            data[tag.name]['count'] = subjects_count

        resources_count = Resource.objects.filter(tags = tag).count()
        if resources_count > 0:
            if data.get(tag.name):
                data[tag.name]['count'] = data[tag.name]['count']  + resources_count
            else:
                data[tag.name] = {'name': tag.name}
                data[tag.name]['count'] = resources_count

    data = sorted(data.values(), key = lambda x: x['count'], reverse=True )
    data = data[:30] #get top 30 tags
    return JsonResponse(data, safe= False) 


def heatmap(request):
    return None



"""
Subject view that returns a list of the most used subjects     """


def most_acessed_subjects(request):
    data = {} #empty response

    data = Log.objects.filter(resource = 'subject')
    subjects = {}
    for datum in data:
        if datum.context:
            subject_id = datum.context['subject_id']
            if subject_id in subjects.keys():
                subjects[subject_id]['count']  = subjects[subject_id]['count'] + 1
            else:
                subjects[subject_id] = {'name': datum.context['subject_name'], 'count':0 }


    #order the values of the dictionary by the count in descendent order
    subjects = sorted(subjects.values(), key = lambda x: x['count'], reverse=True )
    subjects = subjects[:30]

    return JsonResponse(subjects, safe=False)



def most_accessed_categories(request):
    return None

def most_accessed_resource_kind(request):
    return None


def get_users_log(request):
    fifty_users = Log.objects.values('user_id').annotate(count = Count('user_id')).order_by('-count')[:50]
    fifty_users = list(fifty_users)
    for user in fifty_users:
        user_object = User.objects.get(id=user['user_id'])
        user['image'] = user_object.image_url
        user['user'] = user_object.social_name
    return JsonResponse(fifty_users, safe=False)