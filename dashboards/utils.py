from datetime import datetime, timedelta
from django.utils import formats, timezone
from django.core.urlresolvers import reverse

from subjects.models import Tag
from topics.models import Resource
from log.models import Log

from notifications.models import Notification

from pendencies.models import Pendencies

from notifications.utils import get_resource_users

from django.db.models import Q

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

            notifies = Notification.objects.filter(user = user, task = pendency).order_by("-creation_date")

            if notifies.count() > 0:
                last = notifies[0]

                if not last.meta is None:
                    item["date"]["delay"] = formats.date_format(last.meta, "m/d/Y H:i")
                else:
                    item["date"]["delay"] = ""

        graph.append(item)

    return graph

def getAccessedTags(subject, user):
    tags = Tag.objects.all()

    data = []

    logs = Log.objects.filter(datetime__date__gte = datetime.now() - timedelta(days = 7))

    for tag in tags:
        if not tag.name == '':
            resources = Resource.objects.filter(tags = tag, topic__subject = subject)
            
            qtd = 0
            qtd_my = 0

            item = {}
            
            item["tag_name"] = tag.name
            item["details_url"] = reverse('dashboards:tag_accessess', args = (tag.id, subject.slug, user.email,), kwargs = {})
            
            if resources.count() > 0:
                conds = Q()
            
                for res in resources:
                    conds.add(Q(context__contains = {res._my_subclass+'_id': res.id}), Q.OR)

                query = logs.filter(Q(component = 'resources') & conds)

                qtd = qtd + query.count()
                qtd_my = qtd_my + query.filter(user_id = user.id).count()

                item["qtd_access"] = qtd
                item["qtd_my_access"] = qtd_my
            
                data.append(item)

    return data

def getTagAccessess(subject, tag, user):
    resources = Resource.objects.filter(tags = tag, topic__subject = subject)

    logs = Log.objects.filter(datetime__date__gte = datetime.now() - timedelta(days = 7))

    data = []

    for resource in resources:
        item = {}
        
        item["resource_name"] = resource.name

        history = logs.filter(component = 'resources', context__contains = {resource._my_subclass + '_id': resource.id})

        item["qtd_access"] = history.count()
        item["qtd_my_access"] = history.filter(user_id = user.id).count()
        item["access_url"] = resource.access_link()
    
        data.append(item)

    return data
