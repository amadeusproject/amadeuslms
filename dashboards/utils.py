from datetime import datetime
from django.utils import formats, timezone

from log.models import Log

from notifications.models import Notification

from pendencies.models import Pendencies

from notifications.utils import get_resource_users

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
