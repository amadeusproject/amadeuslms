""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import render

from django.views import generic
from django.db.models import Count
from django.core.urlresolvers import reverse_lazy

from subjects.models import Tag, Subject
from topics.models import Resource, Topic
from users.models import User
from django.http import HttpResponse, JsonResponse
from log.models import Log
import operator
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404, redirect

from datetime import date, timedelta, datetime
import calendar
from collections import OrderedDict


from mural.models import Comment


def most_used_tags(request):
   

    data = get_most_used_tags()
    data = sorted(data.values(), key = lambda x: x['count'], reverse=True )
    data = data[:15] #get top 15 tags
    return JsonResponse(data, safe= False) 

def get_most_used_tags():

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
    return data


def most_active_users_in_a_month(request):
    params = request.GET
    month = params['month']
    year = params.get('year')
    days = get_days_of_the_month(month, year)
    if year is None:
        year = date.today().year
    mappings = {_('January'): 1, _('February'): 2, _('March'): 3, _('April'): 4, _('May'): 5, _('June'): 6, _('July'): 7
    , _('August'): 8, _('September'): 9, _('October'): 10, _('November'): 11, _('December'): 12}
    
    days_list = []
    for day in days:
        built_date = date(int(year), mappings[_(month)],  day)
        days_list.append(built_date)
    data = activity_in_timestamp(days_list, params = params)
    
    data = [{"day": day.day, "count": day_count} for day, day_count in data.items()]
    data = sorted(data, key =lambda x: x['day'])
    
    return JsonResponse(data, safe=False)


def activity_in_timestamp(days, **kwargs):
    data = OrderedDict()

    params = kwargs.get('params')
    for day in days:
        if params.get('category_id'):
            category_id = params['category_id']
            day_count = Log.objects.filter(datetime__date = day, context__contains = {"category_id" : int(category_id)}).count()
        else:
            day_count = Log.objects.filter(datetime__date = day).count()
        data[day] = day_count

    return data



def get_days_of_the_month(month, year = date.today().year):
 
    #get current year
    if year is  None:
        year = date.today().year
    mappings = {_('January'): 1, _('February'): 2, _('March'): 3, _('April'): 4, _('May'): 5, _('June'): 6, _('July'): 7
    , _('August'): 8, _('September'): 9, _('October'): 10, _('November'): 11, _('December'): 12}
  
    c = calendar.Calendar()
    days = c.itermonthdays(int(year), mappings[_(month)])
    days_set = set()
    for day in days:
        days_set.add(day)

    days_set.remove(0) #because 0 is not aan actual day from that month
    return days_set 

"""
Subject view that returns a list of the most used subjects     """


def most_accessed_subjects(request):

    subjects = get_log_count_of_resource(resource='subject')
    #order the values of the dictionary by the count in descendent order
    subjects = sorted(subjects.values(), key = lambda x: x['count'], reverse=True )
    subjects = subjects[:5]

    return JsonResponse(subjects, safe=False)

def get_log_count_of_resource(resource = ''):

    data = Log.objects.filter(resource = resource)
    items = {}
    for datum in data:
        if datum.context:
            item_id = datum.context[resource + '_id']
            if item_id in items.keys():
                items[item_id]['count'] = items[item_id]['count'] + 1
            else:
                items[item_id] = {'name': datum.context[resource+'_name'], 'count': 1}
    return items


def most_accessed_categories(request):

    categories = get_log_count_of_resource('category')

   

    categories = sorted(categories.values(), key = lambda x: x['count'], reverse = True)
    categories = categories[:5]
    return JsonResponse(categories, safe= False)


def get_resource_subclasses_count():
    """
        get the amount of objects in each sub_class of resource
    """
    resources = Resource.objects.distinct()
    data = {}
    for resource in resources:
        key = resource.__dict__['_my_subclass']
        if key in data.keys():
            data[key]['count'] = data[key]['count'] + 1
        else:
            data[key] = {'name': key, 'count': 1}

    return data


def most_accessed_resource_kind(request):

    data = get_resource_subclasses_count()

    data = sorted(data.values(), key = lambda x: x['count'], reverse= True)
    mapping = {}
    mapping['pdffile'] = str(_('PDF File'))
    mapping['goals'] = str(_('Topic Goals'))
    mapping['link'] = str(_('Link to Website'))
    mapping['filelink'] = str(_('File Link'))
    mapping['webconference'] = str(_('Web Conference'))
    mapping['ytvideo'] = str(_('YouTube Video'))
    mapping['webpage'] = str(_('WebPage'))

    data = [ {'name': mapping[resource['name']] , 'count': resource['count']} for resource in data]
    data =  data[:5]
    return JsonResponse(data, safe=False)


def most_active_users(request):
    fifty_users = Log.objects.values('user_id').annotate(count = Count('user_id')).order_by('-count')[:50]
    fifty_users = list(fifty_users)
    for user in fifty_users:
        user_object = User.objects.get(id=user['user_id'])
        user['image'] = user_object.image_url
        user['user'] = user_object.social_name
    return JsonResponse(fifty_users, safe=False)






def get_days_of_the_week_log(request):
  
    params = request.GET
    date = params['date']
    date = datetime.strptime( date, '%m/%d/%Y')
    days = get_days_of_the_week(date)
    data = activity_in_timestamp(days, params = params)
    print(data)
    #mapping of number to days
    mapping = {0: _("Mon"), 1: _("Tue"), 2: _("Wed"), 3: _("Thu"), 4: _("Fri"), 5: _("Sat"), 6: _("Sun")}
    #datas = [{"day": day.weekday(), "count": day_count} for day, day_count in data.items()]
    data = [{"day": mapping[day.weekday()], "count": day_count} for day, day_count in data.items()]

    return JsonResponse(data, safe= False)

def get_days_of_the_week(date):

    days_set = []
    days_set.append(date)
    for j in range(1, 7):
        days_set.append(date + timedelta(days=j))
    return days_set



def category_tags(request):
    category_id = request.GET['category_id']
    data = most_tags_inside_category(category_id)
    data = sorted(data.values(), key = lambda x: x['count'], reverse=True )
    data = data[:15] #get top 15 tags
    return JsonResponse(data, safe=False)

def most_tags_inside_category(category_id):
    tags = Tag.objects.all()
    data = {}
    #grab all references to that tag
    for tag in tags:
        subjects_count =  Subject.objects.filter(tags = tag, category__id = category_id).count()
        if  subjects_count > 0:
            data[tag.name] = {'name': tag.name}
            data[tag.name]['count'] = subjects_count

        subjects = Subject.objects.filter(category__id = category_id)
        topics = Topic.objects.filter(subject__in= subjects)
        if topics.count() > 0 :
            resources_count = Resource.objects.filter(tags = tag, topic__in = topics).count()

            if resources_count > 0:
                if data.get(tag.name):
                    data[tag.name]['count'] = data[tag.name]['count']  + resources_count
                else:
                    data[tag.name] = {'name': tag.name}
                    data[tag.name]['count'] = resources_count
    return data


def get_amount_of_comments(request):
    params = request.GET
    #init_date = params.get('init_date')
    #end_date = params.get('end_date')
    init_date = "04/20/2017"
    end_date = "06/09/2017"
    init_date = datetime.strptime( init_date, '%m/%d/%Y')
    end_date = datetime.strptime(end_time, '%m/%d/%Y')
    day_count = (end_date - init_date).days + 1
    data = {}
    for i in range(day_count):
        single_day = init_date + timedelta(i)
        if params.get('category_id'):
            category_id = int(params['category_id'])
            data[single_day] = Mural.objects.filter(space__id = category_id, create_date = single_day).count()
        else:
            data[single_day] = Comment.objects.filter(create_date = single_day).count()

    data_finished = [{date:key, count:value} for key, value in data.items()]
    return JsonResponse(data_finished, safe=False)