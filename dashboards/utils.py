import calendar
import os
from datetime import date, datetime, timedelta
from django.utils import formats, timezone
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.core.urlresolvers import reverse
from django.utils.formats import get_format
from django.utils.translation import ugettext_lazy as _

from subjects.models import Tag, Subject, Log_Consultas
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
from itertools import islice


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


def general_monthly_users_activity(data_ini, data_end):
    period = get_days_in_period(data_ini, data_end)

    usersList = User.objects.filter(
        Cond(subject_student__isnull=False)
        | Cond(professors__isnull=False)
        | Cond(coordinators__isnull=False)
    ).distinct()

    data = list()
    searchs = []
    days = []

    period = sorted(period)

    for day in period:
        searchs.append(
            count_general_daily_access(
                list(usersList.values_list("id", flat=True)), day
            )
        )

        days.append(day)

    if searchs:
        res = multi_search(searchs)

        studentsList = list(
            usersList.filter(subject_student__isnull=False)
            .distinct()
            .values_list("id", flat=True)
        )
        teachersList = list(
            usersList.filter(professors__isnull=False)
            .distinct()
            .values_list("id", flat=True)
        )
        coordinatorsList = list(
            usersList.filter(coordinators__isnull=False)
            .distinct()
            .values_list("id", flat=True)
        )

        accessess = [x.to_dict()["hits"] for x in res]

        users = set()
        dates_set = set()

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

                    if log["user_id"] in studentsList:
                        if log["user_id"] not in teachersList:
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
                    if log["user_id"] in teachersList:
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

                    elif log["user_id"] in coordinatorsList:
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
        if has_category_permissions(user, category):
            my_categories.append(category)

    return my_categories


def generalUsersAccess(dataIni, dataEnd):
    data = []

    usersList = User.objects.filter(
        Cond(subject_student__isnull=False)
        | Cond(professors__isnull=False)
        | Cond(coordinators__isnull=False)
    ).distinct()

    searchs = []
    userAccess = []

    for user in usersList:
        searchs.append(count_user_interactions(user.id, dataIni, dataEnd))
        userAccess.append(user_last_interaction(user.id))

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()["hits"] for x in res]

        userAccessRes = None

        if userAccess:
            userAccessRes = multi_search(userAccess)

        for i, user in enumerate(usersList):
            interactions = accessess[i]["total"]["value"]

            item = {}

            if user.coordinators.count() > 0:
                item["teacher"] = 1
            elif user.professors.count() > 0:
                item["teacher"] = 0
            else:
                item["teacher"] = 2

            item["count"] = interactions
            item["image"] = user.image_url
            item["user"] = user.fullname()
            item["user_id"] = user.id
            item["link_profile"] = reverse(
                "chat:profile", args=(), kwargs={"email": user.email},
            )
            item["link_chat"] = reverse(
                "chat:talk", args=(), kwargs={"email": user.email},
            )
            item["status"], item["status_text"] = userStatus(user, userAccessRes)

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

    usersList = (
        User.objects.filter(
            Cond(subject_student__isnull=False)
            | Cond(professors__isnull=False)
            | Cond(coordinators__isnull=False)
        )
        .distinct()
        .values_list("id", flat=True)
    )

    period = sorted(period)

    usersList = list(usersList)

    data = list()
    searchs = []
    days = []

    for day in period:
        datetime = date_to_datetime(day)
        searchs.append(count_logs_in_day(usersList, str(datetime).split()[0]))
        days.append(day)

    minimun = math.inf
    maximun = 0
    total = 0

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()["hits"] for x in res]
        users = set()
        dates_set = set()

        period = list(dict.fromkeys(period))

        for i, access in enumerate(accessess):
            value = access["total"]["value"]
            time = period[i].strftime("%d/%m/%Y")
            data.append({"x": time, "y": value})

            minimun = min(minimun, value)
            maximun = max(maximun, value)

            total += value

    return data, minimun, maximun, total


def active_users_qty(request_user, data_ini, data_end):
    logs = list()
    cont = 0

    studentsList = User.objects.filter(subject_student__isnull=False).distinct()
    teachersList = User.objects.filter(professors__isnull=False).distinct()

    totalStudents = studentsList.count()
    totalTeachers = teachersList.count()
    activeStudents = 0
    activeTeachers = 0

    searchs = []

    for student in studentsList:
        searchs.append(user_last_interaction_in_period(student.id, data_ini, data_end))

    for teacher in teachersList:
        searchs.append(user_last_interaction_in_period(teacher.id, data_ini, data_end))

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()["hits"] for x in res]

        lastIndex = 0

        for i in range(0, totalStudents):
            entry = accessess[i]

            if entry:
                interactions = entry["total"]["value"]

                if interactions > 0:
                    activeStudents += 1

            lastIndex = i

        if lastIndex > 0:
            lastIndex += 1

        for i in range(0, totalTeachers):
            entry = accessess[i + lastIndex]

            if entry:
                interactions = entry["total"]["value"]

                if interactions > 0:
                    activeTeachers += 1

    data = {
        "total_students": totalStudents,
        "active_students": activeStudents,
        "total_teachers": totalTeachers,
        "active_teachers": activeTeachers,
    }

    return data


def functiontable(dataIni, dataEnd):
    data = {}
    categories_data = []
    subjects_data = []
    resources_data = []

    searchs = []

    usersList = (
        User.objects.filter(
            Cond(subject_student__isnull=False)
            | Cond(professors__isnull=False)
            | Cond(coordinators__isnull=False)
        )
        .distinct()
        .values_list("id", flat=True)
    )

    usersList = list(usersList)

    categories = Category.objects.filter(visible=True).order_by("slug").distinct()
    subjects = (
        Subject.objects.filter(
            visible=True, category__id__in=categories.values_list("id", flat=True)
        )
        .order_by("slug")
        .distinct()
    )
    resources = (
        Resource.objects.filter(
            visible=True, topic__subject__id__in=subjects.values_list("id", flat=True)
        )
        .order_by("slug")
        .distinct()
    )

    for category in categories:
        searchs.append(
            count_categories_logs_period(category, usersList, dataIni, dataEnd)
        )

    for subject in subjects:
        searchs.append(count_subject_logs_period(subject, usersList, dataIni, dataEnd))

    for resource in resources:
        searchs.append(
            count_resources_logs_period(resource, usersList, dataIni, dataEnd)
        )

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()["hits"] for x in res]

        lastIndex = 0

        for i, category in enumerate(categories):
            total = accessess[lastIndex + i]["total"]["value"]

            categories_data.append(
                {
                    "cat_name": category.name,
                    "access": total,
                    "link": reverse(
                        "subjects:cat_view", args=(), kwargs={"slug": category.slug}
                    ),
                }
            )

            lastIndex = i

        if lastIndex > 0:
            lastIndex += 1

        subjectsLastIndex = lastIndex

        for i, subject in enumerate(subjects):
            total = accessess[lastIndex + i]["total"]["value"]

            subjects_data.append(
                {
                    "name": subject.name,
                    "access": total,
                    "category": subject.category.name,
                    "link": reverse(
                        "subjects:view", args=(), kwargs={"slug": subject.slug}
                    ),
                }
            )

            subjectsLastIndex = i + lastIndex

        if subjectsLastIndex > 0:
            lastIndex = subjectsLastIndex + 1
        else:
            lastIndex = subjectsLastIndex

        for i, resource in enumerate(resources):
            total = accessess[lastIndex + i]["total"]["value"]

            resources_data.append(
                {
                    "name": resource.name,
                    "access": total,
                    "link": resource.access_link(),
                }
            )

    data = {
        "categories": categories_data,
        "subjects": subjects_data,
        "resources": resources_data,
    }

    return data


def date_to_datetime(dt: date, hour=0, minute=0, second=0) -> datetime:

    return datetime(dt.year, dt.month, dt.day, hour, minute, second)


"""
def xml_users(request_user, data_ini, data_end):
    categories = my_categories(request_user)
    subjects = (
        Subject.objects.filter(category__in=categories).order_by("slug").distinct()
    )
    teachersList = []
    studentsList = []

    teachersLastInteractionQuery = []
    studentsLastInteractionQuery = []
    users = Log_Consultas.objects.filter(datetime__isnull=True)
    logs = Log_Consultas.objects.filter(
        datetime__date__gte=data_ini, datetime__date__lte=data_end
    )

    workbook = xlwt.Workbook()
    activeTeachersWorksheet = workbook.add_sheet(u"Professores Ativos")
    activeTeachersWorksheet.write(0, 0, u"Professor")
    activeTeachersWorksheet.write(0, 1, u"Nome dos assuntos em que é professor")

    inactiveTeachersWorksheet = workbook.add_sheet(u"Professores Inativos")
    inactiveTeachersWorksheet.write(0, 0, u"Professor")
    inactiveTeachersWorksheet.write(0, 1, u"Nome dos assuntos em que é professor")
    users_teacher = logs.filter(is_teacher=True).distinct("user_id").distinct("subject")
    ac_teachers = []
    ac_teachers_subjects = {}
    inac_teachers = []
    inac_teachers_subjects = {}
    for log in users_teacher:
        if log.user_id not in ac_teachers:
            ac_teachers.append(log.user_id)
            ac_teachers_subjects[log.user_id] = [log.subject]
        else:
            ac_teachers_subjects[log.user_id].append(log.subject)
    for teacher in users.filter(is_teacher=True):
        if teacher.user_id not in ac_teachers:
            if teacher.user_id not in inac_teachers:
                inac_teachers.append(teacher.user_id)
            for sub in teacher.teacher_subjects.all():
                if teacher.user_id in inac_teachers_subjects.keys():
                    if sub not in list(inac_teachers_subjects[teacher.user_id]):
                        inac_teachers_subjects[teacher.user_id].append(sub)
                else:
                    inac_teachers_subjects[teacher.user_id] = [sub]
        else:
            subs = ac_teachers_subjects[teacher.user_id]
            if teacher.teacher_subjects.all().count() > len(subs):
                if teacher.user_id not in inac_teachers:
                    inac_teachers.append(teacher.user_id)
                for sub in teacher.teacher_subjects.all():
                    if sub not in list(ac_teachers_subjects[teacher.user_id]()):
                        if teacher.user_id in inac_teachers_subjects.keys():
                            if sub not in list(inac_teachers_subjects[teacher.user_id]):
                                inac_teachers_subjects[teacher.user_id].append(sub)
                        else:
                            inac_teachers_subjects[teacher.user_id] = [sub]

    inactivesLine = activesLine = 1
    for user in users:
        if user.is_teacher == True:
            if user.user_id in ac_teachers:
                activeTeachersWorksheet.write(activesLine, 0, user.user)
                activeTeachersWorksheet.write(
                    activesLine,
                    1,
                    ", ".join(str(sub) for sub in ac_teachers_subjects[user.user_id]),
                )
                activesLine += 1
            else:
                inactiveTeachersWorksheet.write(inactivesLine, 0, user.user)
                inactiveTeachersWorksheet.write(
                    inactivesLine,
                    1,
                    ", ".join(str(sub) for sub in inac_teachers_subjects[user.user_id]),
                )

                inactivesLine += 1

    activeStudentsWorksheet = workbook.add_sheet(u"Estudantes Ativos")
    activeStudentsWorksheet.write(0, 0, u"Estudante")
    activeStudentsWorksheet.write(0, 1, u"Nome dos assuntos em que é estudante")

    inactiveStudentsWorksheet = workbook.add_sheet(u"Estudantes Inativos")
    inactiveStudentsWorksheet.write(0, 0, u"Estudante")
    inactiveStudentsWorksheet.write(0, 1, u"Nome dos assuntos em que é estudante")
    users_students = (
        logs.filter(is_student=True).distinct("user_id").distinct("subject")
    )
    ac_students = []
    ac_students_subjects = {}
    inac_students = []
    inac_students_subjects = {}
    for log in users_students:
        if log.user_id not in ac_teachers:
            ac_students.append(log.user_id)
            ac_students_subjects[log.user_id] = [log.subject]
        else:
            ac_students_subjects[log.user_id].append(log.subject)

    for student in users.filter(is_student=True):
        if student.user_id not in ac_students:
            if student.user_id not in inac_students:
                inac_students.append(student.user_id)
            for sub in student.student_subjects.all():
                if student.user_id in inac_students_subjects.keys():
                    if sub not in list(inac_students_subjects[student.user_id]):
                        inac_students_subjects[student.user_id].append(sub)
                else:
                    inac_students_subjects[student.user_id] = [sub]
        else:
            subs = ac_students_subjects[student.user_id]
            if student.student_subjects.all().count() > len(subs):
                if student.user_id not in inac_students:
                    inac_students.append(student.user_id)
                for sub in student.student_subjects.all():
                    if sub not in list(ac_students_subjects[student.user_id]()):
                        if student.user_id in inac_students_subjects.keys():
                            if sub not in list(inac_students_subjects[student.user_id]):
                                inac_students_subjects[student.user_id].append(sub)
                        else:
                            inac_students_subjects[student.user_id] = [sub]
    activesLine = inactivesLine = 1
    for user in users:
        if user.is_student == True:
            if user.user_id in ac_students:
                activeStudentsWorksheet.write(activesLine, 0, user.user)
                activeStudentsWorksheet.write(
                    activesLine,
                    1,
                    ", ".join(str(sub) for sub in ac_students_subjects[user.user_id]),
                )

                activesLine += 1
            else:
                inactiveStudentsWorksheet.write(inactivesLine, 0, user.user)
                inactiveStudentsWorksheet.write(
                    inactivesLine,
                    1,
                    ", ".join(str(sub) for sub in inac_students_subjects[user.user_id]),
                )

                inactivesLine += 1

    path1 = os.path.join(settings.BASE_DIR, "dashboards")
    path2 = os.path.join(path1, "sheets")
    path3 = os.path.join(path2, "xls")

    filename = request_user.fullname().replace(" ", "_") + ".xls"
    folder_path = os.path.join(path3, filename)

    if not os.path.isdir(path3):
        os.makedirs(path3)

    workbook.save(folder_path)

    filepath = os.path.join(
        "dashboards", os.path.join("sheets", os.path.join("xls", filename))
    )

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
"""


def xml_users(request_user, data_ini, data_end):
    categories = my_categories(request_user)
    subjects = (
        Subject.objects.filter(category__in=categories).order_by("slug").distinct()
    )

    teachersList = []
    studentsList = []

    teachersLastInteractionQuery = []
    studentsLastInteractionQuery = []
    for subject in subjects:
        for professor in subject.professor.all():
            if not professor in teachersList:
                teachersLastInteractionQuery.append(
                    user_last_interaction_in_period(professor.id, data_ini, data_end)
                )
                teachersList.append(professor)

        for student in subject.students.all():
            if not student in studentsList:
                studentsLastInteractionQuery.append(
                    user_last_interaction_in_period(student.id, data_ini, data_end)
                )
                studentsList.append(student)

    workbook = xlwt.Workbook()
    activeTeachersWorksheet = workbook.add_sheet(u"Professores Ativos")
    activeTeachersWorksheet.write(0, 0, u"Professor")
    activeTeachersWorksheet.write(0, 1, u"Nome dos assuntos em que é professor")

    inactiveTeachersWorksheet = workbook.add_sheet(u"Professores Inativos")
    inactiveTeachersWorksheet.write(0, 0, u"Professor")
    inactiveTeachersWorksheet.write(0, 1, u"Nome dos assuntos em que é professor")

    if teachersLastInteractionQuery:
        res = multi_search(teachersLastInteractionQuery)

        activesLine = 1
        inactivesLine = 1

        for i, teacher in enumerate(teachersList):
            if i < len(res):
                entry = res[i]

                if entry:
                    activeTeachersWorksheet.write(activesLine, 0, teacher.fullname())
                    activeTeachersWorksheet.write(
                        activesLine,
                        1,
                        ", ".join(str(sub.name) for sub in teacher.professors.all()),
                    )

                    activesLine += 1
                else:
                    inactiveTeachersWorksheet.write(
                        inactivesLine, 0, teacher.fullname()
                    )
                    inactiveTeachersWorksheet.write(
                        inactivesLine,
                        1,
                        ", ".join(str(sub.name) for sub in teacher.professors.all()),
                    )

                    inactivesLine += 1

    activeStudentsWorksheet = workbook.add_sheet(u"Estudantes Ativos")
    activeStudentsWorksheet.write(0, 0, u"Estudante")
    activeStudentsWorksheet.write(0, 1, u"Nome dos assuntos em que é estudante")

    inactiveStudentsWorksheet = workbook.add_sheet(u"Estudantes Inativos")
    inactiveStudentsWorksheet.write(0, 0, u"Estudante")
    inactiveStudentsWorksheet.write(0, 1, u"Nome dos assuntos em que é estudante")

    if studentsLastInteractionQuery:
        res = multi_search(studentsLastInteractionQuery)

        activesLine = 1
        inactivesLine = 1

        for i, student in enumerate(studentsList):
            if i < len(res):
                entry = res[i]

                if entry:
                    activeStudentsWorksheet.write(activesLine, 0, student.fullname())
                    activeStudentsWorksheet.write(
                        activesLine,
                        1,
                        ", ".join(
                            str(sub.name) for sub in student.subject_student.all()
                        ),
                    )

                    activesLine += 1
                else:
                    inactiveStudentsWorksheet.write(
                        inactivesLine, 0, student.fullname()
                    )
                    inactiveStudentsWorksheet.write(
                        inactivesLine,
                        1,
                        ", ".join(
                            str(sub.name) for sub in student.subject_student.all()
                        ),
                    )

                    inactivesLine += 1

    path1 = os.path.join(settings.BASE_DIR, "dashboards")
    path2 = os.path.join(path1, "sheets")
    path3 = os.path.join(path2, "xls")

    filename = request_user.fullname().replace(" ", "_") + ".xls"
    folder_path = os.path.join(path3, filename)

    if not os.path.isdir(path3):
        os.makedirs(path3)

    workbook.save(folder_path)

    filepath = os.path.join(
        "dashboards", os.path.join("sheets", os.path.join("xls", filename))
    )

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


def load_logs():

    all_logs = Log.objects.all()
    categories = Category.objects.all()
    subjects = Subject.objects.all()
    teachersList = []
    studentsList = []
    coordinator_list = []
    admins = User.objects.filter(is_staff=True)
    admin_list = []
    teacher_subjects = {}
    student_subjects = {}

    for subject in subjects:
        for (
            professor
        ) in subject.professor.all():  ## List all subjects for teachers as a dict
            if professor.id not in teachersList:
                teachersList.append(professor.id)
            if professor.id not in teacher_subjects.keys():
                teacher_subjects[professor.id] = [subject]
            else:
                if subject not in teacher_subjects[professor.id]:
                    teacher_subjects[professor.id].append(subject)

        for (
            student
        ) in subject.students.all():  ## List all subjects for students as a dict
            if student.id not in studentsList:
                studentsList.append(student.id)
            if student.id not in student_subjects.keys():
                student_subjects[student.id] = [subject]
            else:
                if subject not in student_subjects[student.id]:
                    student_subjects[student.id].append(subject)
    for category in categories:  ## List all coordinators
        for coordenador in category.coordinators.all():
            if coordenador.id not in coordinator_list:
                coordinator_list.append(coordenador.id)
    for admin in admins:  ## List all admins
        if admin.id not in admin_list:
            admin_list.append(admin.id)
    objs = list()

    for logs in all_logs:

        is_admin = bool()
        is_teacher = bool()
        is_student = bool()
        is_coordinator = bool()
        if logs.user_id in admin_list:
            is_admin = True
        else:
            is_admin = False
        if logs.user_id in teachersList:
            is_teacher = True
        else:
            is_teacher = False

        if logs.user_id in studentsList:
            is_student = True
        else:
            is_student = False

        if logs.user_id in coordinator_list:
            is_coordinator = True
        else:
            is_coordinator = False

        log = Log_Consultas()
        log.user = logs.user
        log.user_id = logs.user_id
        log.user_email = logs.user_email
        log.component = logs.component
        log.context = logs.context
        log.action = logs.action
        log.resource = logs.resource

        log.datetime = logs.datetime
        log.is_admin = is_admin
        log.is_teacher = is_teacher
        log.is_student = is_student
        log.is_coordinator = is_coordinator
        if logs.context:
            if logs.context != {}:
                if "subject_id" in logs.context.keys():
                    id = logs.context["subject_id"]
                    try:
                        sub = Subject.objects.get(id=id)
                    except:
                        sub = None

                    if sub is not None:
                        log.subject = sub

        objs.append(log)

    print("Saving...")
    log_bulk = Log_Consultas.objects.bulk_create(objs=objs)
    print("Saved.")

    users = User.objects.all().distinct()
    objs = list()
    for user in users:  ## Add all users as teacher or student or coordinator or admin
        is_admin = bool()
        is_teacher = bool()
        is_student = bool()
        is_coordinator = bool()
        if user.id in admin_list:
            is_admin = True
        else:
            is_admin = False
        if user.id in teachersList:
            is_teacher = True
        else:
            is_teacher = False

        if user.id in studentsList:
            is_student = True
        else:
            is_student = False

        if user.id in coordinator_list:
            is_coordinator = True
        else:
            is_coordinator = False

        log = Log_Consultas()
        log.user = user
        log.user_id = user.id
        log.user_email = user.email
        log.is_admin = is_admin
        log.is_teacher = is_teacher
        log.is_student = is_student
        log.is_coordinator = is_coordinator

        objs.append(log)

    print("Saving2...")
    log_bulk = Log_Consultas.objects.bulk_create(objs=objs)
    print("Saved.")

    logs = Log_Consultas.objects.filter(datetime__isnull=True)
    if logs:
        for log in logs:  ## Add all users and list yours subjects as teacher or student

            if log.user_id in teacher_subjects.keys():
                for a in teacher_subjects[log.user_id]:
                    log.teacher_subjects.add(a.id)

            if log.user_id in student_subjects.keys():
                for a in student_subjects[log.user_id]:
                    log.student_subjects.add(a.id)


def add_daily_logs():

    all_logs = Log.objects.all(
        datetime__date__gte=timezone.now() - timedelta(days=1),
        datetime__date__lte=timezone.now(),
    )

    categories = Category.objects.all()
    subjects = Subject.objects.all()
    teachersList = []
    studentsList = []
    coordinator_list = []
    admins = User.objects.filter(is_staff=True)
    admin_list = []
    teacher_subjects = {}
    student_subjects = {}

    for subject in subjects:
        for professor in subject.professor.all():
            if professor.id not in teachersList:
                teachersList.append(professor.id)
            if professor.id not in teacher_subjects.keys():
                teacher_subjects[professor.id] = [subject]
            else:
                if subject not in teacher_subjects[professor.id]:
                    teacher_subjects[professor.id].append(subject)

        for student in subject.students.all():
            if student.id not in studentsList:
                studentsList.append(student)
            if student.id not in student_subjects.keys():
                student_subjects[student.id] = [subject]
            else:
                if subject not in student_subjects[student.id]:
                    student_subjects[student.id].append(subject)
    for category in categories:
        for coordenador in category.coordinators.all():
            if coordenador.id not in coordinator_list:
                coordinator_list.append(coordenador.id)
    for admin in admins:
        if admin.id not in admin_list:
            admin_list.append(admin.id)
    objs = list()

    for logs in all_logs:

        is_admin = bool()
        is_teacher = bool()
        is_student = bool()
        is_coordinator = bool()
        if logs.user_id in admin_list:
            is_admin = True
        else:
            is_admin = False
        if logs.user_id in teachersList:
            is_teacher = True
        else:
            is_teacher = False

        if logs.user_id in studentsList:
            is_student = True
        else:
            is_student = False

        if logs.user_id in coordinator_list:
            is_coordinator = True
        else:
            is_coordinator = False

        log = Log_Consultas()
        log.user = logs.user
        log.user_id = logs.user_id
        log.user_email = logs.user_email
        log.component = logs.component
        log.context = logs.context
        log.action = logs.action
        log.resource = logs.resource

        log.datetime = logs.datetime
        log.is_admin = is_admin
        log.is_teacher = is_teacher
        log.is_student = is_student
        log.is_coordinator = is_coordinator
        if logs.context:
            if logs.context != {}:
                if "subject_id" in logs.context.keys():
                    id = logs.context["subject_id"]
                    try:
                        sub = Subject.objects.get(id=id)
                    except:
                        sub = None
                    if sub is not None:
                        log.subject = sub
        objs.append(log)

    batch_size = 10000

    print("Saving...")
    while True:
        batch = list(islice(objs, batch_size))
        if not batch:
            break
        log_bulk = Log_Consultas.objects.bulk_create(batch, batch_size)
    print("Saved.")

    users = User.objects.all().distinct()
    objs = list()
    new_users = list()
    for user in users:
        logs = (
            Log_Consultas.objects.filter(datetime__isnull=True)
            .filter(user_id=user.id)
            .count()
        )
        if logs < 1:
            new_users.append(user.id)
            is_admin = bool()
            is_teacher = bool()
            is_student = bool()
            is_coordinator = bool()
            if user.id in admin_list:
                is_admin = True
            else:
                is_admin = False
            if user.id in teachersList:
                is_teacher = True
            else:
                is_teacher = False

            if user.id in studentsList:
                is_student = True
            else:
                is_student = False

            if user.id in coordinator_list:
                is_coordinator = True
            else:
                is_coordinator = False

            log = Log_Consultas()
            log.user = user
            log.user_id = user.id
            log.user_email = user.email
            log.is_admin = is_admin
            log.is_teacher = is_teacher
            log.is_student = is_student
            log.is_coordinator = is_coordinator

            objs.append(log)

    print("Saving2...")
    while True:
        batch = list(islice(objs, batch_size))
        if not batch:
            break
        log_bulk = Log_Consultas.objects.bulk_create(batch, batch_size)
    print("Saved.")

    logs = Log_Consultas.objects.filter(datetime__isnull=True).filter(
        user_id__in=new_users
    )
    if logs:
        for log in logs:
            if log.user_id in teacher_subjects.keys():
                for a in teacher_subjects[log.user_id]:
                    log.teacher_subjects.add(a.id)

            if log.user_id in student_subjects.keys():
                for a in student_subjects[log.user_id]:
                    log.student_subjects.add(a.id)
