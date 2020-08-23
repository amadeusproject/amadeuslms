import calendar
import os
from datetime import date, datetime, timedelta
from django.utils import formats, timezone
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.core.urlresolvers import reverse
from django.utils.formats import get_format
from django.utils.translation import ugettext_lazy as _

from subjects.models import Tag, Subject
from topics.models import Topic, Resource
from log.models import Log
from bulletin.models import Bulletin
from file_link.models import FileLink
from goals.models import Goals
from links.models import Link
from mural.models import SubjectPost
from pdf_file.models import PDFFile
from questionary.models import Questionary
from goals.models import Goals
from webpage.models import Webpage
from webconference.models import Webconference

from youtube_video.models import YTVideo
from notifications.models import Notification

from pendencies.models import Pendencies, PendencyDone

from notifications.utils import get_resource_users

from django.db.models import Q as Cond, Max, Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse, Http404
from collections import OrderedDict

from gtts import gTTS
from mutagen.mp3 import MP3

import operator, math

from log.search import *

from categories.models import Category
from amadeus.permissions import has_category_permissions

from django.shortcuts import get_object_or_404
from users.models import User
import xlwt

def done_percent(pendency):
    users = get_resource_users(pendency.resource)
    usersDone = PendencyDone.objects.filter(
        pendency=pendency, student__id__in=users.values_list("id", flat=True)
    ).count()

    number_users = users.count()

    if usersDone == 0 or number_users == 0:
        done = 0
    else:
        done = (usersDone * 100) / number_users

    return done


def get_pend_graph(user, subject):
    pendencies = Pendencies.objects.filter(
        resource__topic__subject=subject,
        begin_date__gte=subject.init_date,
        resource__visible=True,
    )
    graph = []

    for pendency in pendencies:
        item = {}
        item["date"] = {}
        item["date"]["start"] = formats.date_format(pendency.begin_date, "m/d/Y H:i")
        item["date"]["startDate"] = pendency.begin_date
        item["date"]["end"] = formats.date_format(pendency.end_date, "m/d/Y H:i")
        item["date"]["endDate"] = pendency.end_date
        item["date"]["delay"] = (
            formats.date_format(pendency.limit_date, "m/d/Y H:i")
            if pendency.limit_date
            else "infinity"
        )
        item["date"]["delayDate"] = pendency.limit_date

        item["action"] = pendency.get_action_display()
        item["name"] = pendency.resource.name

        if pendency.begin_date <= timezone.now():
            item["percent"] = done_percent(pendency) / 100
        else:
            item["percent"] = 0

        item["access_link"] = str(pendency.resource.access_link())

        users = get_resource_users(pendency.resource)
        subject_begin_date = pendency.resource.topic.subject.init_date
        pend_action = pendency.action
        resource_type = pendency.resource._my_subclass
        resource_key = resource_type + "_id"
        resource_id = pendency.resource.id

        item["done"] = False
        item["doneLate"] = False

        if user in users:
            has_action = PendencyDone.objects.filter(pendency=pendency, student=user)

            item["done"] = has_action.exists()
            item["doneLate"] = False

            if item["done"]:
                pDone = has_action.first()

                item["doneLate"] = pDone.late

        graph.append(item)

    return graph


def getAccessedTags(subject, user):

    tags = Tag.objects.filter(resource_tags__topic__subject=subject).distinct().all()

    data = []
    searchs = []
    for tag in tags:
        if not tag.name == "":
            resources = Resource.objects.filter(tags__id=tag.id, topic__subject=subject)

            if resources.count() > 0:
                searchs.append(count_logs(resources))
                searchs.append(count_logs(resources, user.id))
                tag.access = 1
            else:
                tag.access = 0

    if len(searchs) > 0:
        res = multi_search(searchs)

    counter = 0

    for tag in tags:
        if not tag.name == "":
            item = {}
            item["tag_name"] = tag.name
            item["details_url"] = reverse(
                "dashboards:tag_accessess",
                args=(tag.id, subject.slug, user.email),
                kwargs={},
            )

            if tag.access == 1:
                item["qtd_access"] = res[counter].to_dict()["hits"]["total"]["value"]
                item["qtd_my_access"] = res[counter + 1].to_dict()["hits"]["total"][
                    "value"
                ]

                counter = counter + 2
            else:
                item["qtd_access"] = 0
                item["qtd_my_access"] = 0
            data.append(item)

    return data


def getAccessedTagsPeriod(subject, user, data_ini="", data_end=""):

    tags = Tag.objects.filter(resource_tags__topic__subject=subject).distinct().all()
    if data_ini == "":
        data_ini = "now-30d"
    if data_end == "":
        data_end = "now"
    data = []
    searchs = []
    for tag in tags:
        if not tag.name == "":
            resources = Resource.objects.filter(tags__id=tag.id, topic__subject=subject)

            if resources.count() > 0:
                searchs.append(count_logs_period(resources, data_ini, data_end))
                searchs.append(
                    count_logs_period(resources, data_ini, data_end, user.id)
                )
                tag.access = 1

            else:
                tag.access = 0

    if len(searchs) > 0:
        res = multi_search(searchs)

    counter = 0

    for tag in tags:
        if not tag.name == "":
            item = {}
            item["tag_name"] = tag.name
            item["details_url"] = reverse(
                "dashboards:tag_accessess_period",
                args=(tag.id, subject.slug, user.email, data_ini, data_end),
                kwargs={},
            )

            if tag.access == 1:
                item["qtd_access"] = res[counter].to_dict()["hits"]["total"]["value"]
                item["qtd_my_access"] = res[counter + 1].to_dict()["hits"]["total"][
                    "value"
                ]

                counter = counter + 2
            else:
                item["qtd_access"] = 0
                item["qtd_my_access"] = 0
            data.append(item)

    return data


def getTagAccessess(subject, tag, user):
    resources = Resource.objects.filter(tags=tag, topic__subject=subject)

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
            item["qtd_access"] = res[counter].to_dict()["hits"]["total"]["value"]
            item["qtd_my_access"] = res[counter + 1].to_dict()["hits"]["total"]["value"]
            item["access_url"] = resource.access_link()

            counter = counter + 2

            data.append(item)

    return data


def getTagAccessessPeriod(subject, tag, user, data_ini, data_end):
    resources = Resource.objects.filter(tags=tag, topic__subject=subject)

    if data_ini == "":
        data_ini = "now-30d"
    if data_end == "":
        data_end = "now"

    data = []
    searchs = []
    for resource in resources:
        searchs.append(resource_accessess_period(resource, data_ini, data_end))
        searchs.append(resource_accessess_period(resource, data_ini, data_end, user.id))

    if searchs:
        res = multi_search(searchs)

        counter = 0

        for resource in resources:
            item = {}

            item["resource_name"] = resource.name
            item["qtd_access"] = res[counter].to_dict()["hits"]["total"]["value"]
            item["qtd_my_access"] = res[counter + 1].to_dict()["hits"]["total"]["value"]
            item["access_url"] = resource.access_link()

            counter = counter + 2
            data.append(item)

    return data


def getOtherIndicators(subject, user):
    logs = Log.objects.filter(
        datetime__date__gte=timezone.now() - timedelta(days=6),
        datetime__date__lte=timezone.now(),
    )

    data = []
    searchs = []

    students = subject.students.all()

    # First indicator
    for student in students:
        if student.id != user.id:
            searchs.append(count_access_subject(subject.id, student.id))

    searchs.append(count_access_subject(subject.id, user.id))

    item = {}

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()["hits"]["total"]["value"] for x in res]

        my_access = accessess[-1]

        accessess = list(dict.fromkeys(accessess))

        accessess.sort()

        qtd_results = len(accessess)

        if qtd_results > 5:
            item["percentil_1"] = accessess[math.floor(qtd_results * 0.25)]
            item["percentil_2"] = accessess[math.floor(qtd_results * 0.5)]
            item["percentil_3"] = accessess[math.floor(qtd_results * 0.75)]
            item["percentil_4"] = accessess[math.floor(qtd_results * 0.9)]
        else:
            item["percentil_1"] = accessess[-5] if len(accessess) == 5 else 0
            item["percentil_2"] = accessess[-4] if len(accessess) > 3 else 0
            item["percentil_3"] = accessess[-3] if len(accessess) > 2 else 0
            item["percentil_4"] = accessess[-2] if len(accessess) > 1 else 0

        item["max_access"] = accessess[-1]
        item["my_access"] = my_access
    else:
        item["percentil_1"] = 0
        item["percentil_2"] = 0
        item["percentil_3"] = 0
        item["percentil_4"] = 0
        item["max_access"] = 0
        item["my_access"] = 0

    data.append(item)

    searchs = []

    # Second indicator
    for student in students:
        if student.id != user.id:
            searchs.append(count_diff_days(subject.id, student.id))

    searchs.append(count_diff_days(subject.id, user.id))

    item = {}

    if searchs:
        res = multi_search(searchs)

        accessess = [
            len(x.to_dict()["aggregations"]["dt"]["buckets"])
            if "aggregations" in x.to_dict()
            else 0
            for x in res
        ]

        my_access = accessess[-1]

        accessess = list(dict.fromkeys(accessess))

        accessess.sort()

        qtd_results = len(accessess)

        if qtd_results > 5:
            item["percentil_1"] = accessess[math.floor(qtd_results * 0.25)]
            item["percentil_2"] = accessess[math.floor(qtd_results * 0.5)]
            item["percentil_3"] = accessess[math.floor(qtd_results * 0.75)]
            item["percentil_4"] = accessess[math.floor(qtd_results * 0.9)]
        else:
            item["percentil_1"] = accessess[-5] if len(accessess) == 5 else 0
            item["percentil_2"] = accessess[-4] if len(accessess) > 3 else 0
            item["percentil_3"] = accessess[-3] if len(accessess) > 2 else 0
            item["percentil_4"] = accessess[-2] if len(accessess) > 1 else 0

        item["max_access"] = accessess[-1]
        item["my_access"] = my_access
    else:
        item["percentil_1"] = 0
        item["percentil_2"] = 0
        item["percentil_3"] = 0
        item["percentil_4"] = 0
        item["max_access"] = 0
        item["my_access"] = 0

    data.append(item)

    searchs = []

    # Third indicator
    for student in students:
        if student.id != user.id:
            searchs.append(count_access_resources(subject.id, student.id))

    searchs.append(count_access_resources(subject.id, user.id))

    item = {}

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()["hits"]["total"]["value"] for x in res]

        my_access = accessess[-1]

        accessess = list(dict.fromkeys(accessess))

        accessess.sort()

        qtd_results = len(accessess)

        if qtd_results > 5:
            item["percentil_1"] = accessess[math.floor(qtd_results * 0.25)]
            item["percentil_2"] = accessess[math.floor(qtd_results * 0.5)]
            item["percentil_3"] = accessess[math.floor(qtd_results * 0.75)]
            item["percentil_4"] = accessess[math.floor(qtd_results * 0.9)]
        else:
            item["percentil_1"] = accessess[-5] if len(accessess) == 5 else 0
            item["percentil_2"] = accessess[-4] if len(accessess) > 3 else 0
            item["percentil_3"] = accessess[-3] if len(accessess) > 2 else 0
            item["percentil_4"] = accessess[-2] if len(accessess) > 1 else 0

        item["max_access"] = accessess[-1]
        item["my_access"] = my_access
    else:
        item["percentil_1"] = 0
        item["percentil_2"] = 0
        item["percentil_3"] = 0
        item["percentil_4"] = 0
        item["max_access"] = 0
        item["my_access"] = 0

    data.append(item)

    # Fourth indicator
    resources_access = logs.filter(
        component="resources",
        action="view",
        context__contains={"subject_id": subject.id},
    )

    s = [student.id for student in students]
    accessess = []

    students_sets = {key: set() for key in s}

    for entry in resources_access.filter(user_id__in=s).all():
        resource_name = "goals" if entry.resource == "my_goals" else entry.resource

        students_sets[entry.user_id].add(entry.context["%s_id" % (resource_name)])

    students_accessess = [len(students_sets[x]) for x in students_sets]

    students_accessess.sort()

    item = {}

    if students_accessess:
        my_access = set()

        for entry in resources_access.filter(user_id=user.id).all():
            resource_name = "goals" if entry.resource == "my_goals" else entry.resource

            my_access.add(entry.context["%s_id" % (resource_name)])

        qtd_results = len(students_accessess)

        if qtd_results > 5:
            item["percentil_1"] = students_accessess[math.floor(qtd_results * 0.25)]
            item["percentil_2"] = students_accessess[math.floor(qtd_results * 0.5)]
            item["percentil_3"] = students_accessess[math.floor(qtd_results * 0.75)]
            item["percentil_4"] = students_accessess[math.floor(qtd_results * 0.9)]
        else:
            item["percentil_1"] = (
                students_accessess[-5] if len(students_accessess) == 5 else 0
            )
            item["percentil_2"] = (
                students_accessess[-4] if len(students_accessess) > 3 else 0
            )
            item["percentil_3"] = (
                students_accessess[-3] if len(students_accessess) > 2 else 0
            )
            item["percentil_4"] = (
                students_accessess[-2] if len(students_accessess) > 1 else 0
            )

        item["max_access"] = students_accessess[-1]
        item["my_access"] = len(my_access)
    else:
        item["percentil_1"] = 0
        item["percentil_2"] = 0
        item["percentil_3"] = 0
        item["percentil_4"] = 0
        item["max_access"] = 0
        item["my_access"] = 0

    data.append(item)

    # Fifth indicator

    pend = Pendencies.objects.filter(
        resource__topic__subject=subject.id,
        resource__visible=True,
        begin_date__date__lt=timezone.now(),
        end_date__date__gte=timezone.now() - timedelta(days=6),
    )
    accessess = []

    item = {}

    if pend.count() > 0:
        for student in students:
            if student.id != user.id:
                accessess.append(
                    PendencyDone.objects.filter(
                        pendency__id__in=pend.values_list("id", flat=True),
                        late=False,
                        student=student,
                    ).count()
                )

        accessess.append(
            PendencyDone.objects.filter(
                pendency__id__in=pend.values_list("id", flat=True),
                late=False,
                student=user,
            ).count()
        )

        if accessess:
            my_access = accessess[-1]

            accessess = list(dict.fromkeys(accessess))
            accessess.sort()

            qtd_results = len(accessess)

            if qtd_results > 5:
                item["percentil_1"] = accessess[math.floor(qtd_results * 0.25)]
                item["percentil_2"] = accessess[math.floor(qtd_results * 0.5)]
                item["percentil_3"] = accessess[math.floor(qtd_results * 0.75)]
                item["percentil_4"] = accessess[math.floor(qtd_results * 0.9)]
            else:
                item["percentil_1"] = accessess[-5] if len(accessess) == 5 else 0
                item["percentil_2"] = accessess[-4] if len(accessess) > 3 else 0
                item["percentil_3"] = accessess[-3] if len(accessess) > 2 else 0
                item["percentil_4"] = accessess[-2] if len(accessess) > 1 else 0

            item["max_access"] = accessess[-1]
            item["my_access"] = my_access
    else:
        item["percentil_1"] = 0
        item["percentil_2"] = 0
        item["percentil_3"] = 0
        item["percentil_4"] = 0
        item["max_access"] = 0
        item["my_access"] = 0

    data.append(item)

    return data


def accessResourceCount(subject, dataIni, dataEnd):
    resources = Resource.objects.filter(topic__subject=subject)
    if dataIni == "":
        dataIni = "now-30d"
    if dataEnd == "":
        dataEnd = "now"
    data = []
    searchs = []
    searchs = []
    for resource in resources:
        searchs.append(resource_accessess_period(resource, dataIni, dataEnd))

    if searchs:
        res = multi_search(searchs)
        counter = 0

        for resource in resources:
            item = {}
            item["resource_name"] = resource.name
            item["qtd_access"] = res[counter].to_dict()["hits"]["total"]["value"]
            item["access_url"] = resource.access_link()
            counter = counter + 1
            data.append(item)
        data.sort(key=lambda x: x["qtd_access"], reverse=True)
    return data


def studentsAccess(subject, dataIni, dataEnd):
    students = subject.students.all()

    if dataIni == "":
        dataIni = "now-30d"

    if dataEnd == "":
        dataEnd = "now"

    data = []
    searchs = []

    for student in students:
        searchs.append(
            count_access_subject_period(subject.id, student.id, dataIni, dataEnd)
        )

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()["hits"]["total"]["value"] for x in res]

        for i, access in enumerate(accessess):
            item = {}

            obj = students[i]

            item["count"] = access
            item["image"] = obj.image_url
            item["user"] = str(obj)
            item["user_id"] = obj.id
            item["link"] = reverse(
                "dashboards:view_subject_student",
                args=(),
                kwargs={"slug": subject.slug, "email": obj.email},
            )

            data.append(item)

        data.sort(key=lambda x: x["count"], reverse=True)

    return data


def parse_date(date_str):
    """Parse date from string by DATE_INPUT_FORMATS of current language"""
    for item in get_format("DATE_INPUT_FORMATS"):
        try:
            return datetime.strptime(date_str, item).date()
        except (ValueError, TypeError):
            continue

    return None


def get_days_in_period(data_ini, data_end):
    c = calendar.Calendar()

    days_set = set()

    dates_start = c.itermonthdates(data_ini.year, data_ini.month)

    for day in dates_start:
        if data_ini <= day <= data_end:
            days_set.add(day)

    months_btw = data_end.month - data_ini.month
    year_btw = data_ini.year

    if months_btw < 0:
        months_btw = months_btw * (-1)

    month_b = data_ini.month

    for i in range(0, months_btw):
        month_b = data_ini.month + i

        if month_b > 12:
            month_b = 1
            year_btw = year_btw + 1

        dates_btw = c.itermonthdates(year_btw, month_b)

        for day in dates_btw:
            if data_ini <= day <= data_end:
                days_set.add(day)

    dates_end = c.itermonthdates(data_end.year, data_end.month)

    for day in dates_end:
        if data_ini <= day <= data_end:
            days_set.add(day)

    return days_set


def monthly_users_activity(subject, data_ini, data_end):
    period = get_days_in_period(data_ini, data_end)

    students = subject.students.all().values_list("id", flat=True)

    data = list()

    searchs = []
    days = []

    for day in period:
        searchs.append(count_daily_access(subject.id, list(students), day))
        days.append(day)

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()["hits"] for x in res]

        users = set()
        dates_set = set()

        for access in accessess:
            for hits in access["hits"]:
                log = hits["_source"]

                accessDate = parse_datetime(log["datetime"])
                dates_set.add(accessDate.date())

                utuple = (
                    str(accessDate.day)
                    + "-"
                    + str(accessDate.month)
                    + "-"
                    + str(accessDate.year),
                    log["user_id"],
                )

                if not utuple in users:
                    users.add(utuple)

                    data.append(
                        {
                            "year": accessDate.year,
                            "month": accessDate.month - 1,
                            "day": accessDate.day,
                            "hour": accessDate.hour,
                            "user_id": log["user_id"],
                            "value": 1,
                            "count": 1,
                        }
                    )

        for day in period:
            if not day in dates_set:
                dates_set.add(day)

                data.append(
                    {
                        "year": day.year,
                        "month": day.month - 1,
                        "day": day.day,
                        "hour": 0,
                        "user_id": 0,
                        "value": 0,
                        "count": 0,
                    }
                )

        data = sorted(data, key=lambda x: (x["month"], x["day"]))

    return data



def general_monthly_users_activity(subjects, data_ini, data_end):
    period = get_days_in_period(data_ini, data_end)
    students_list = list()
    teacher_list = list()
    coordinators_list = list()
    subject_list = list()
    data = list()
    data2 = list()
    searchs = []
    days = []
    admins = (
        User.objects.filter(is_staff=True)
        .values_list("id", flat=True)
        .order_by("id")
        .distinct()
    )
    for subject in subjects:
        students = subject.students.all().values_list("id", flat=True)
        professores = subject.professor.all().values_list("id", flat=True)
        category = subject.category
        coordinators = category.coordinators.all().values_list("id", flat=True)
        coordinators_list.extend(coordinators)
        students_list.extend(students)
        teacher_list.extend(professores)

    for day in period:
        searchs.append(count_general_daily_access(list(students_list), day))
        searchs.append(count_general_daily_access(list(teacher_list), day))
        searchs.append(count_general_daily_access(list(coordinators_list), day))
        searchs.append(count_general_daily_access(list(admins), day))

        days.append(day)

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()["hits"] for x in res]

        users = set()
        dates_set = set()
        cont = 0
        cont2 = 0
        for i, access in enumerate(accessess):
            for hits in access["hits"]:
                log = hits["_source"]

                accessDate = parse_datetime(log["datetime"])
                dates_set.add(accessDate.date())

                utuple = (
                    str(accessDate.day)
                    + "-"
                    + str(accessDate.month)
                    + "-"
                    + str(accessDate.year),
                    log["user_id"],
                )
                if not utuple in users:
                    users.add(utuple)

                    if log["user_id"] in students_list:
                        if log["user_id"] not in teacher_list:
                            data.append(
                                {
                                    "year": accessDate.year,
                                    "month": accessDate.month - 1,
                                    "day": accessDate.day,
                                    "hour": accessDate.hour,
                                    "user_id": log["user_id"],
                                    "value": 1,
                                    "count": 1,
                                    "teacher": 0,
                                }
                            )
                    if log["user_id"] in teacher_list:
                        data.append(
                            {
                                "year": accessDate.year,
                                "month": accessDate.month - 1,
                                "day": accessDate.day,
                                "hour": accessDate.hour,
                                "user_id": log["user_id"],
                                "value": 1,
                                "count": 1,
                                "teacher": 1,
                            }
                        )

                    elif log["user_id"] in coordinators_list:
                        data.append(
                            {
                                "year": accessDate.year,
                                "month": accessDate.month - 1,
                                "day": accessDate.day,
                                "hour": accessDate.hour,
                                "user_id": log["user_id"],
                                "value": 1,
                                "count": 1,
                                "teacher": 2,
                            }
                        )
                    elif log["user_id"] in admins:
                        data.append(
                            {
                                "year": accessDate.year,
                                "month": accessDate.month - 1,
                                "day": accessDate.day,
                                "hour": accessDate.hour,
                                "user_id": log["user_id"],
                                "value": 1,
                                "count": 1,
                                "teacher": 4,
                            }
                        )

        for day in period:
            if not day in dates_set:
                dates_set.add(day)
                data.append(
                    {
                        "year": day.year,
                        "month": day.month - 1,
                        "day": day.day,
                        "hour": 0,
                        "user_id": 0,
                        "value": 0,
                        "count": 0,
                        "teacher": 0,
                    }
                )
                data.append(
                    {
                        "year": day.year,
                        "month": day.month - 1,
                        "day": day.day,
                        "hour": 0,
                        "user_id": 0,
                        "value": 0,
                        "count": 0,
                        "teacher": 1,
                    }
                )

        data = sorted(data, key=lambda x: (x["month"], x["day"]))

    return data


def my_categories(user):
    my_categories = []
    categories = Category.objects.filter()
    for category in categories:
        if has_category_permissions(user, category) or has:
            my_categories.append(category)

    return my_categories


def generalUsersAccess(
    subjects, dataIni, dataEnd,
):
    category_list = []
    students_ids = list()
    teachers_id = list()
    coordinators_id = list()
    admins = admins = User.objects.filter(is_staff=True).distinct()
    admins_id = []
    
    if dataIni == "":
        # dataIni = "now-30d"
        dataIni = "now-7d"

    if dataEnd == "":
        dataEnd = "now"
    data = []
    for j, subject in enumerate(subjects):
        students = list()
        teachers = list()
        students_list = subject.students.all()
        category_list = subject.category
        teachers_list = subject.professor.all()
        
        coordinators_list = subject.category.coordinators.all()

        searchs = []
        cont = 0
        cont2 = 0
        users = []

        userAccess = []
        for professor in teachers_list:
            if professor.id not in teachers_id:
                teachers_id.append(professor.id)
                cont+= 1
                teachers.append(professor)

                searchs.append(
                    # count_access_subject_period(subject.id, professor.id, dataIni, dataEnd)
                    count_general_access_period(professor.id, dataIni, dataEnd)
                )
                userAccess.append(user_last_interaction(professor.id))
        cont2=cont
        for student in students_list:
            if student.id not in students_ids:
                if student.id not in teachers_id:
                    students_ids.append(student.id)
                    cont2+=1
                    students.append(student)
                    searchs.append(
                        # count_access_subject_period(subject.id, student.id, dataIni, dataEnd)
                        count_general_access_period(student.id, dataIni, dataEnd)
                    )
                    userAccess.append(user_last_interaction(student.id))
     
        
        # cont3 = cont2
        # for coordenador in coordinators_list:
        #     if coordenador.id not in coordinators_id:
        #         if coordenador.id not in teachers_id:
        #             if coordenador.id not in admins_id:
        #                 cont3+=1
        #                 searchs.append(
        #                     # count_access_subject_period(subject.id, coordenador.id, dataIni, dataEnd)
        #                     count_general_access_period(coordenador.id, dataIni, dataEnd)
        #                 )
        if j == 0:
            for admin in admins:
                searchs.append(
                    # count_access_subject_period(subject.id, admin.id, dataIni, dataEnd)
                    count_general_access_period(admin.id, dataIni, dataEnd)
                )
                userAccess.append(user_last_interaction(admin.id))
        if searchs:
            res = multi_search(searchs)

            userAccessRes = None

            if userAccess:
                userAccessRes = multi_search(userAccess)
          
            
            accessess = [x.to_dict()["hits"]["total"]["value"] for x in res]
   
            for i, access in enumerate(accessess):
                item = {}
                if i < cont:
                    obj = teachers[i]
                    item["teacher"] = 1
                elif i < cont2:
                    obj = students[i-cont]
                    if obj.id in teachers_id:
                        teachers_id.append(obj.id)
                        item["teacher"] = 1
                    else: 
                        item["teacher"] = 0
                
                # elif i < cont3:
                #     obj = coordinators_list[i - cont2]
                #     if obj.id in teachers_id:
                #         teachers_id.append(obj.id)
                #         item["teacher"] = 1
                #     else: 
                #         item["teacher"] = 2
                elif j == 0:
                    obj = admins[i-cont2]
                    if obj.id in teachers_id:
                        teachers_id.append(obj.id)
                        item["teacher"] = 1
                    else: 
                        item["teacher"] = 2
                    admins_id.append(obj.id)
                item["count"] = access
                item["image"] = obj.image_url
                item["user"] = str(obj)
                item["user_id"] = obj.id
                item["link_profile"] = reverse(
                    "chat:profile", args=(), kwargs={"email": obj.email},
                )
                item["link_chat"] = reverse(
                    "chat:talk", args=(), kwargs={"email": obj.email},
                )
                item["status"], item["status_text"] = userStatus(obj, userAccessRes)

                data.append(item)
        data.sort(key=lambda x: x["count"], reverse=True)

    return data

def userStatus(user, lastInteractions):
    expire_time = settings.SESSION_SECURITY_EXPIRE_AFTER

    status = "inactive"
    status_text = _("Offline")

    if not lastInteractions is None:
        lastEntry = next(
            (
                item
                for item in lastInteractions
                if len(item.hits) > 0 and item.hits[0].user_id == user.id
            ),
            None,
        )

        if not lastEntry is None:
            timeDelta = datetime.now() - datetime.strptime(
                lastEntry.hits[0].datetime[:-6], "%Y-%m-%dT%H:%M:%S.%f"
            )

            if (
                lastEntry.hits[0].action != "logout"
                and timeDelta.total_seconds() < expire_time
            ):
                status = "active"
                status_text = _("Online")

    return status, status_text


def general_logs(user, data_ini, data_end):
    period = get_days_in_period(data_ini, data_end)
    logs_data = list()
    logs = Log.objects.filter()
    # subjects = []
    # categories = my_categories(user)
    # subs = Subject.objects.filter(category__in = categories)

    # for subject in subs:
    #     logs_data.append(logs.filter(
    #         context__contains={"subject_id": subject.id},
    #     ))

    data = list()
    searchs = []
    days = []

    for day in period:
        # day = day.strftime('%d/%m/%Y %H:%M')
        datetime = date_to_datetime(day)
        searchs.append(count_daily_general_logs_access1(datetime))
        searchs.append(count_daily_general_logs_access2(datetime))
        days.append(day)

    # if searchs:
    #     res = multi_search(searchs)

    #     accessess = [x.to_dict()["hits"]["total"]["value"] for x in res]
    #     users = set()
    #     dates_set = set()
    #     accessess = list(dict.fromkeys(accessess))
    #     period = list(dict.fromkeys(period))
    #     print(len(accessess))
    #     print(len(period))
    #     for i, access in enumerate(accessess):
    #         time = period[i].strftime('%d/%m/%Y')
    #         print(time)
    #         data.append({'x': time, 'y':access})
    #         print(data[i])
    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()["hits"] for x in res]
        users = set()
        dates_set = set()

        period = list(dict.fromkeys(period))
        sum = 0
        a = 0
        for i, access in enumerate(accessess):

            sum += access["total"]["value"]
            if i % 2 == 0:

                time = period[a].strftime("%d/%m/%Y")
                data.append({"x": time, "y": sum})
                sum = 0
                a += 1

    return data


def active_users_qty(request_user, data_ini, data_end):
    logs = list()
    cont = 0
    categories = my_categories(request_user)
    subjects = (
        Subject.objects.filter(category__in=categories).order_by("slug").distinct()
    )

    total_students = 0
    total_teachers = 0
    ac_students = 0
    ac_teachers = 0
    id_students = []
    id_teachers = []
    all_students = []
    all_teachers = []

    for sub in subjects:
        sub = get_object_or_404(Subject, slug=sub.slug)
        students = sub.students.all().values_list("id", flat=True)
        professores = sub.professor.all().values_list("id", flat=True)

        for student in students:
            if student not in id_students:
                all_students.append(
                    user_last_interaction_in_period(student, data_ini, data_end)
                )
                id_students.append(student)
                total_students += 1

        for professor in professores:
            if professor not in id_teachers:
                all_teachers.append(
                    user_last_interaction_in_period(professor, data_ini, data_end)
                )
                id_teachers.append(professor)
                total_teachers += 1

    res = multi_search(all_students)
    for i, student in enumerate(all_students):
        entry = res[i]
        if entry:
            ac_students += 1

    res = multi_search(all_teachers)
    for i, professor in enumerate(all_teachers):
        entry = res[i]
        if entry:
            ac_teachers += 1

    data = {
        "total_students": total_students,
        "active_students": ac_students,
        "total_teachers": total_teachers,
        "active_teachers": ac_teachers,
    }
    return data


def functiontable(categories, dataIni, dataEnd):
    data = {}
    categories_data = []
    subjects_data = []
    resources_data = []
    subs = list()
    searchs1 = list()
    searchs2 = list()
    searchs3 = list()
    searchs4 = list()
    searchs5 = list()
    searchs6 = list()
    searchs7 = list()
    searchs8 = list()
    for category in categories:
        res = []
        cont = 0
        subjects = (
            Subject.objects.filter(category=category)
            .filter(visible=True)
            .order_by("slug")
            .distinct()
        )
        searchs = list()
        accessess = []
        for subject in subjects:
            searchs.append(
                count_general_access_subject_period(subject.id, dataIni, dataEnd)
            )
        subs.append(subject)
        if searchs:
            res = multi_search(searchs)

            accessess = [x.to_dict()["hits"]["total"]["value"] for x in res]

            for i, access in enumerate(accessess):
                item = {}
                obj = subjects[i]
                cont += access
                subjects_data.append(
                    {
                        "name": obj.name,
                        "access": access,
                        "category": category.name,
                        "link": reverse(
                            "subjects:view", args=(), kwargs={"slug": obj.slug}
                        ),
                    }
                )
        categories_data.append(
            {
                "cat_name": category.name,
                "access": cont,
                "link": reverse(
                    "subjects:cat_view", args=(), kwargs={"slug": category.slug}
                ),
            }
        )
    searchs1.append(count_general_resource_logs_period(subs, dataIni, dataEnd))
    names_resources = {
        "pdffile": "Arquivo PDF",
        "pdf_file": "Arquivo PDF",
        "bulletin": "Boletim do Tópico",
        "ytvideo": "Vídeo do YouTube",
        "filelink": "Link para arquivo",
        "link": "Link para Site",
        "goals": "Metas do Tópico",
        "webpage": "Página Web",
        "questionary": "Questionário",
        "webconference": "Web conferência",
        "my_goals": "Metas do Tópico",
    }
    if searchs1:
        res1 = multi_search(searchs1)
        accessess1 = [x.to_dict()["hits"] for x in res1]
        list_resources = list()
        for i, access in enumerate(accessess1):
            for hits in access["hits"]:
                log = hits["_source"]
                item = {}
                if log["resource"] in names_resources.keys():
                    resources_data.append(
                        {
                            "name": names_resources[log["resource"]],
                            "access": 1,
                            "link": log,
                        }
                    )

    data = {
        "categories": categories_data,
        "subjects": subjects_data,
        "resources": resources_data,
    }
    return data

def xml_users(request_user, data_ini, data_end):
    categories = my_categories(request_user)
    subjects = (
        Subject.objects.filter(category__in=categories).order_by("slug").distinct()
    )

    total_students = 0
    total_teachers = 0
    ac_students = {}
    ac_teachers = {}
    inac_students = {}
    inac_teachers = {}
    a_students = []
    a_teachers = []
    i_teachers = []
    i_students = []
    id_students = []
    id_teachers = []
    all_students = []
    all_teachers = []

    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(u"Professores Ativos")
    worksheet.write(0, 0, u"Professor")
    worksheet.write(0, 1, u"N° de Assuntos")
    worksheet.write(0, 2, u"Nº de Assuntos com registros")
    worksheet.write(0, 3, u"Nº de Assuntos sem registros")
    worksheet.write(0, 4, u"Nome de Assuntos com registros")
    worksheet.write(0, 5, u"Nome de Assuntos sem registros")
    line = 1

    for sub in subjects:
        sub = get_object_or_404(Subject, slug=sub.slug)
        professores = sub.professor.all()
        for professor in professores:
                all_teachers.append(
                    user_last_interaction_in_period(professor.id, data_ini, data_end)
                )
                id_teachers.append(professor)
                total_teachers += 1
    
        res = multi_search(all_teachers)
        

        for i, teacher in enumerate(id_teachers):
            entry = res[i]

            if entry:
                if teacher not in a_teachers:
                    a_teachers.append(teacher)
                    ac_teachers[teacher.id]=[sub]
                else:
                    if sub not in ac_teachers[teacher.id]:
                        ac_teachers[teacher.id].append(sub)
            else:
                if teacher not in i_teachers:
                    i_teachers.append(teacher)
                    inac_teachers[teacher.id]=[sub]
                else:
                    if sub not in inac_teachers[teacher.id]:
                        inac_teachers[teacher.id].append(sub)
    i = 0        
    while i < len(a_teachers):
        subs_names= ''
        worksheet.write(line, 0, a_teachers[i].fullname())
        for a in ac_teachers[a_teachers[i].id]:
            subs_names += str(a) + ', ' 
        if a_teachers[i] in inac_teachers.keys():
            total = len(ac_teachers[a_teachers[i].id])+len(inac_teachers[a_teachers[i].id])
            ac = len(ac_teachers[a_teachers[i].id])
            inac = len(inac_teachers[a_teachers[i].id])
        else:
            ac=total = len(ac_teachers[a_teachers[i].id])

            inac = 0
        worksheet.write(line, 1, total)
        worksheet.write(line, 2, ac)
        worksheet.write(line, 3, inac)
        worksheet.write(line, 4, subs_names)
        if inac == 0:
            worksheet.write(line, 5, '')
        else:
            subs_names  = ''
            for a in inac_teachers[a_teachers[i].id]:
                subs_names += str(a) + ', ' 
            worksheet.write(line, 5, subs_names)
        i+=1
        line+=1
    worksheet = workbook.add_sheet(u"Estudantes Ativos")
    worksheet.write(0, 0, u"Estudante")
    worksheet.write(0, 1, u"N° de Assuntos")
    worksheet.write(0, 2, u"Nº de Assuntos com registros")
    worksheet.write(0, 3, u"Nº de Assuntos sem registros")
    worksheet.write(0, 4, u"Nome de Assuntos com registros")
    worksheet.write(0, 5, u"Nome de Assuntos sem registros")
    line = 1

    for sub in subjects:
        sub = get_object_or_404(Subject, slug=sub.slug)
        students = sub.students.all()
        
        for student in students:
            all_students.append(
                user_last_interaction_in_period(student.id, data_ini, data_end)
            )
            id_students.append(student)
            total_students += 1

        res = multi_search(all_students)
        

        for i, student in enumerate(id_students):
            entry = res[i]

            if entry:
                if student not in a_students:
                    a_students.append(student)
                    ac_students[student.id]=[sub]
                else:
                    if sub not in ac_students[student.id]:
                        ac_students[student.id].append(sub)
            else:
                if student not in i_students:
                    i_students.append(student)
                    inac_students[student.id]=[sub]
                else:
                    if sub not in inac_students[student.id]:
                        inac_students[student.id].append(sub)
    i = 0        
    while i < len(a_students):
        subs_names= ''
        worksheet.write(line, 0, a_students[i].fullname())
        for a in ac_students[a_students[i].id]:
            subs_names += str(a) + ', ' 
        if a_students[i] in inac_students.keys():
            total = len(ac_students[a_students[i].id])+len(inac_students[a_students[i].id])
            ac = len(ac_students[a_students[i].id])
            inac = len(inac_students[a_students[i].id])
        else:
            ac=total = len(ac_students[a_students[i].id])

            inac = 0
        worksheet.write(line, 1, total)
        worksheet.write(line, 2, ac)
        worksheet.write(line, 3, inac)
        worksheet.write(line, 4, subs_names)
        if inac == 0:
            worksheet.write(line, 5, '')
        else:
            for a in inac_students[a_students[i].id]:
                subs_names += str(a) + ', ' 
            worksheet.write(line, 5, subs_names)
        i+=1
        line+=1
    worksheet = workbook.add_sheet(u"Estudantes Inativos")
    worksheet.write(0, 0, u"Estudante")
    worksheet.write(0, 1, u"Disciplinas")
    line = 1
    i = 0        
    while i < len(i_students):
        subs_names= ''
        worksheet.write(line, 0, i_students[i].fullname())
        for a in inac_students[i_students[i].id]:
            subs_names += str(a) + ', ' 
        worksheet.write(line, 1, subs_names)
        i+=1
        line+=1
       
    
    # worksheet = workbook.add_sheet(u"Professores Ativos")
    # worksheet.write(0, 0, u"Professor")
    # worksheet.write(0, 1, u"Disciplinas")
    # line = 1

    # for sub in subjects:
    #     sub = get_object_or_404(Subject, slug=sub.slug)
    #     professores = sub.professor.all()
    #     for professor in professores:
    #             all_teachers.append(
    #                 user_last_interaction_in_period(professor.id, data_ini, data_end)
    #             )
    #             id_teachers.append(professor)
    #             total_teachers += 1

    #     res = multi_search(all_teachers)
        
    #     for i, teacher in enumerate(id_teachers):
    #         entry = res[i]
    #         if entry:
    #             ac_teachers.append(teacher)
    #             ac_teachers.append(sub)
    #         else:
    #             inac_teachers.append(teacher)
    #             inac_teachers.append(sub)

    # i = 0        
    # while i < len(ac_teachers):
    #     worksheet.write(line, 0, ac_teachers[i].fullname())
    #     worksheet.write(line, 1, ac_teachers[i+1].name)
    #     i+=2
    #     line+=1
    # worksheet = workbook.add_sheet(u"Professores Inativos")
    # worksheet.write(0, 0, u"Estudante")
    # worksheet.write(0, 1, u"Disciplinas")
    # line = 1
    # i = 0        
    # while i < len(inac_teachers):
    #     worksheet.write(line, 0, inac_teachers[i].fullname())
    #     worksheet.write(line, 1, inac_teachers[i+1].name)
    #     i+=2
    #     line+=1
    
    path1 = os.path.join(settings.BASE_DIR, "dashboards")
    path2 = os.path.join(path1, "sheets")
    path3 = os.path.join(path2, "xls")

    filename = str(request_user) + ".xls"
    folder_path = os.path.join(path3, filename)
    
        # check if the folder already exists
    if not os.path.isdir(path3):
        os.makedirs(path3)

    workbook.save(folder_path)

    filepath = os.path.join(
        "dashboards", os.path.join("sheets", os.path.join("xls", filename))
    )
    print(filepath)
    if not os.path.exists(filepath):
        raise Http404()

    response = HttpResponse(open(filepath, "rb").read())
    response["Content-Type"] = "application/force-download"
    response["Pragma"] = "public"
    response["Expires"] = "0"
    response["Cache-Control"] = "must-revalidate, post-check=0, pre-check=0"
    response["Content-Disposition"] = "attachment; filename=%s" % (filename)
    response["Content-Transfer-Encoding"] = "binary"
    response["Content-Length"] = str(os.path.getsize(filepath))


    return response

def date_to_datetime(
    dt: date,
    hour= 0,
    minute= 0, 
    second= 0) -> datetime:

    return datetime(dt.year, dt.month, dt.day, hour, minute, second)