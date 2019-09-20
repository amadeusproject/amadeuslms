from datetime import datetime, timedelta
from django.utils import formats, timezone
from django.core.urlresolvers import reverse

from subjects.models import Tag
from topics.models import Resource
from log.models import Log

from notifications.models import Notification

from pendencies.models import Pendencies

from notifications.utils import get_resource_users

from django.db.models import Q, Max, Count
from django.db.models.functions import TruncDate

import operator, math

from log.search import *
from subjects.search import tags_all
from topics.search import resources_by_tag

def done_percent(pendency):
    users = get_resource_users(pendency.resource)
    notified = Notification.objects.filter(user__in = users.values_list('id', flat = True), creation_date = datetime.now(), task = pendency).count()
    
    number_users = users.count()

    not_done = (notified * 100) / number_users

    return 100 - not_done

def get_pend_graph(user, subject):
    pendencies = Pendencies.objects.filter(resource__topic__subject = subject, resource__visible = True)
    graph = []

    for pendency in pendencies:
        item = {}
        item["date"] = {}
        item["date"]["start"] = formats.date_format(pendency.begin_date, "m/d/Y H:i")
        item["date"]["end"] = formats.date_format(pendency.end_date, "m/d/Y H:i")
        item["date"]["delay"] = formats.date_format(pendency.limit_date, "m/d/Y H:i") if pendency.limit_date else "infinity"

        item["action"] = pendency.get_action_display()
        item["name"] = pendency.resource.name
        
        if pendency.begin_date <= timezone.now():
            item["percent"] = done_percent(pendency)/100
        else:
            item["percent"] = 0

        item["access_link"] = str(pendency.resource.access_link())

        users = get_resource_users(pendency.resource)
        subject_begin_date = pendency.resource.topic.subject.init_date
        pend_action = pendency.action
        resource_type = pendency.resource._my_subclass
        resource_key = resource_type + "_id"
        resource_id = pendency.resource.id

        if user in users:
            has_action = Log.objects.filter(user_id = user.id, action = pend_action, resource = resource_type, context__contains = {resource_key: resource_id}, datetime__date__gte = subject_begin_date).exists()

            item["done"] = True

            if not has_action:
                item["done"] = False

            """notifies = Notification.objects.filter(user = user, task = pendency).order_by("-creation_date")

            if notifies.count() > 0:
                last = notifies[0]

                if not last.meta is None:
                    item["date"]["delay"] = formats.date_format(last.meta, "m/d/Y H:i")"""

        graph.append(item)

    return graph

def getAccessedTags(subject, user):
    tags = Tag.objects.all()

    data = []
    searchs = []
       
    for tag in tags:
        if not tag.name == '':
            resources = Resource.objects.filter(tags__id = tag.id, topic__subject = subject)

            if resources.count() > 0:
                searchs.append(count_logs(resources))
                searchs.append(count_logs(resources, user.id))
                tag.access = 1
            else:
                tag.access = 0

    res = multi_search(searchs)

    counter = 0
    
    for tag in tags:
        if not tag.name == '':
            item = {}
            
            item["tag_name"] = tag.name
            item["details_url"] = reverse('dashboards:tag_accessess', args = (tag.id, subject.slug, user.email,), kwargs = {})

            if tag.access == 1:
                item["qtd_access"] = res[counter].to_dict()['hits']['total']['value']
                item["qtd_my_access"] = res[counter + 1].to_dict()['hits']['total']['value']
                
                counter = counter + 2
            else:
                item["qtd_access"] = 0
                item["qtd_my_access"] = 0

            data.append(item)
            
    return data

def getTagAccessess(subject, tag, user):
    resources = Resource.objects.filter(tags = tag, topic__subject = subject)

    data = []
    searchs = []

    for resource in resources:
        searchs.append(resource_accessess(resource))
        searchs.append(resource_accessess(resource, user.id))

    if searchs:
        res = multi_search(searchs)

        counter = 0

        for resource in resources:
            item = {}
            
            item["resource_name"] = resource.name
            item["qtd_access"] = res[counter].to_dict()['hits']['total']['value']
            item["qtd_my_access"] = res[counter + 1].to_dict()['hits']['total']['value']
            item["access_url"] = resource.access_link()

            counter = counter + 2
        
            data.append(item)

    return data

def getOtherIndicators(subject, user):
    logs = Log.objects.filter(datetime__date__gte = timezone.now() - timedelta(days = 7), datetime__date__lt = timezone.now())

    data = []
    searchs = []

    students = subject.students.all()

    #First indicator
    for student in students:
        if student.id != user.id:
            searchs.append(count_access_subject(subject.id, student.id))

    searchs.append(count_access_subject(subject.id, user.id))

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()['hits']['total']['value'] for x in res]

        my_access = accessess[-1]

        accessess = list(dict.fromkeys(accessess))
        
        accessess.sort()

        item = {}
        
        qtd_results = len(accessess)

        if qtd_results > 5:
            item['percentil_1'] = accessess[math.floor(qtd_results * 0.25)]
            item['percentil_2'] = accessess[math.floor(qtd_results * 0.5)]
            item['percentil_3'] = accessess[math.floor(qtd_results * 0.75)]
            item['percentil_4'] = accessess[math.floor(qtd_results * 0.9)]
        else:
            item['percentil_1'] = accessess[-5] if len(accessess) == 5 else 0
            item['percentil_2'] = accessess[-4] if len(accessess) > 3 else 0
            item['percentil_3'] = accessess[-3] if len(accessess) > 2 else 0
            item['percentil_4'] = accessess[-2] if len(accessess) > 1 else 0 

        item['max_access'] = accessess[-1]
        item['my_access'] = my_access

        data.append(item)
    
    searchs = []

    #Second indicator
    for student in students:
        if student.id != user.id:
            searchs.append(count_diff_days(subject.id, student.id))

    searchs.append(count_diff_days(subject.id, user.id))

    if searchs:
        res = multi_search(searchs)
            
        accessess = [len(x.to_dict()['aggregations']['dt']['buckets']) if 'aggregations' in x.to_dict() else 0 for x in res]

        my_access = accessess[-1]

        accessess = list(dict.fromkeys(accessess))
        
        accessess.sort()

        item = {}
        
        qtd_results = len(accessess)

        if qtd_results > 5:
            item['percentil_1'] = accessess[math.floor(qtd_results * 0.25)]
            item['percentil_2'] = accessess[math.floor(qtd_results * 0.5)]
            item['percentil_3'] = accessess[math.floor(qtd_results * 0.75)]
            item['percentil_4'] = accessess[math.floor(qtd_results * 0.9)]
        else:
            item['percentil_1'] = accessess[-5] if len(accessess) == 5 else 0
            item['percentil_2'] = accessess[-4] if len(accessess) > 3 else 0
            item['percentil_3'] = accessess[-3] if len(accessess) > 2 else 0
            item['percentil_4'] = accessess[-2] if len(accessess) > 1 else 0 

        item['max_access'] = accessess[-1]
        item['my_access'] = my_access

        data.append(item)

    searchs = []

    #Third indicator
    for student in students:
        if student.id != user.id:
            searchs.append(count_access_resources(subject.id, student.id))

    searchs.append(count_access_resources(subject.id, user.id))

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()['hits']['total']['value'] for x in res]

        my_access = accessess[-1]

        accessess = list(dict.fromkeys(accessess))
        
        accessess.sort()

        item = {}
        
        qtd_results = len(accessess)

        if qtd_results > 5:
            item['percentil_1'] = accessess[math.floor(qtd_results * 0.25)]
            item['percentil_2'] = accessess[math.floor(qtd_results * 0.5)]
            item['percentil_3'] = accessess[math.floor(qtd_results * 0.75)]
            item['percentil_4'] = accessess[math.floor(qtd_results * 0.9)]
        else:
            item['percentil_1'] = accessess[-5] if len(accessess) == 5 else 0
            item['percentil_2'] = accessess[-4] if len(accessess) > 3 else 0
            item['percentil_3'] = accessess[-3] if len(accessess) > 2 else 0
            item['percentil_4'] = accessess[-2] if len(accessess) > 1 else 0 

        item['max_access'] = accessess[-1]
        item['my_access'] = my_access

        data.append(item)

    #Fourth indicator
    resources_access = logs.filter(component = 'resources', context__contains = {'subject_id': subject.id})

    s = [student.id for student in students]

    accessess = resources_access.filter(user_id__in = s).values('resource', 'user_id').annotate(total = Count('resource')) \
        .values('user_id').annotate(total = Count('user_id')).order_by('total').values_list('total', flat = True)
    
    item = {}
    
    if accessess:
        my_access = resources_access.filter(user_id = user.id).values('resource').distinct().count()

        accessess = list(dict.fromkeys(accessess))

        
        qtd_results = len(accessess)

        if qtd_results > 5:
            item['percentil_1'] = accessess[math.floor(qtd_results * 0.25)]
            item['percentil_2'] = accessess[math.floor(qtd_results * 0.5)]
            item['percentil_3'] = accessess[math.floor(qtd_results * 0.75)]
            item['percentil_4'] = accessess[math.floor(qtd_results * 0.9)]
        else:
            item['percentil_1'] = accessess[-5] if len(accessess) == 5 else 0
            item['percentil_2'] = accessess[-4] if len(accessess) > 3 else 0
            item['percentil_3'] = accessess[-3] if len(accessess) > 2 else 0
            item['percentil_4'] = accessess[-2] if len(accessess) > 1 else 0 

        item['max_access'] = accessess[-1]
        item['my_access'] = my_access

    data.append(item)
        
    #Fifth indicator
    pend = Pendencies.objects.filter(resource__topic__subject = subject.id, resource__visible = True, end_date__date__lt = timezone.now(), end_date__date__gte = timezone.now() - timedelta(days = 7))
    accessess = []

    item = {}

    if pend.count() > 0:
        conds = Q()

        for p in pend:
            conds.add((Q(context__contains = {p.resource._my_subclass+'_id': p.resource.id}) & Q(action = p.action)), Q.OR)

        res_access = logs.filter(conds)

        for student in students:
            if student.id != user.id:
                accessess.append(res_access.filter(user_id = student.id).count())

        accessess.append(res_access.filter(user_id = user.id).count())

        if accessess:
            my_access = accessess[-1]

            accessess = list(dict.fromkeys(accessess))
            
            accessess.sort()

            qtd_results = len(accessess)

            if qtd_results > 5:
                item['percentil_1'] = accessess[math.floor(qtd_results * 0.25)]
                item['percentil_2'] = accessess[math.floor(qtd_results * 0.5)]
                item['percentil_3'] = accessess[math.floor(qtd_results * 0.75)]
                item['percentil_4'] = accessess[math.floor(qtd_results * 0.9)]
            else:
                item['percentil_1'] = accessess[-5] if len(accessess) == 5 else 0
                item['percentil_2'] = accessess[-4] if len(accessess) > 3 else 0
                item['percentil_3'] = accessess[-3] if len(accessess) > 2 else 0
                item['percentil_4'] = accessess[-2] if len(accessess) > 1 else 0 

            item['max_access'] = accessess[-1]
            item['my_access'] = my_access

    data.append(item)

    return data