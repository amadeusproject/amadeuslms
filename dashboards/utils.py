import calendar
import os
from datetime import date, datetime, timedelta
from django.utils import formats, timezone
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.core.urlresolvers import reverse
from django.utils.formats import get_format

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

from collections import OrderedDict

from gtts import gTTS
from mutagen.mp3 import MP3

import operator, math

from log.search import *

from categories.models import Category
from amadeus.permissions import has_category_permissions

from django.shortcuts import get_object_or_404
from users.models import User

def done_percent(pendency):
    users = get_resource_users(pendency.resource)
    usersDone = PendencyDone.objects.filter(
        pendency=pendency, student__id__in=users.values_list("id", flat=True)
    ).count()

    number_users = users.count()

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
    subject_list= list()
    data = list()
    data2 = list()
    print("chegou");
    for subject in subjects:
        students = subject.students.all().values_list("id", flat=True)
        professores = subject.professor.all().values_list("id", flat=True)
        students_list.extend(students)
        teacher_list.extend(professores)
        subject_list.append(subject)
        searchs = []
        searchs2 = []
        days = []

    for day in period:
        searchs.append(count_general_daily_access(list(subjects), list(students), day))
        searchs.append(count_general_daily_access(list(subjects), list(professores), day))
        # searchs2.append(count_daily_access(subject.id, list(professores), day))
        days.append(day)
    

    if searchs:
        res = multi_search(searchs)
        # res2 =  multi_search(searchs2)
        
        accessess = [x.to_dict()["hits"] for x in res]
        # accessess2 = [x.to_dict()["hits"] for x in res2]

        users = set()
        dates_set = set()
        
        for i,access in enumerate(accessess):
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
                    if i%2==0:
                        data.append(
                            {
                                "year": accessDate.year,
                                "month": accessDate.month - 1,
                                "day": accessDate.day,
                                "hour": accessDate.hour,
                                "user_id": log["user_id"],
                                "value": 1,
                                "count": 1,
                                "teacher":0,

                            }
                        )
                    else:
                        data.append(
                            {
                                "year": accessDate.year,
                                "month": accessDate.month - 1,
                                "day": accessDate.day,
                                "hour": accessDate.hour,
                                "user_id": log["user_id"],
                                "value": 1,
                                "count": 1,
                                "teacher":1,

                            }
                        )
        
        for day in period:
            if not day in dates_set:
                dates_set.add(day)
                if i%2==0:  
                    data.append(
                        {
                            "year": day.year,
                            "month": day.month - 1,
                            "day": day.day,
                            "hour": 0,
                            "user_id": 0,
                            "value": 0,
                            "count": 0,
                            "teacher":0,
                        }
                    )
                else:
                        data.append(
                        {
                            "year": day.year,
                            "month": day.month - 1,
                            "day": day.day,
                            "hour": 0,
                            "user_id": 0,
                            "value": 0,
                            "count": 0,
                            "teacher":1,
                        }
                    )
    #     users = set()
    #     dates_set = set()


    #     for access in accessess2:
    #         for hits in access["hits"]:
    #             log = hits["_source"]

    #             accessDate = parse_datetime(log["datetime"])
    #             dates_set.add(accessDate.date())

    #             utuple = (
    #                 str(accessDate.day)
    #                 + "-"
    #                 + str(accessDate.month)
    #                 + "-"
    #                 + str(accessDate.year),
    #                 log["user_id"],
    #             )

    #             if not utuple in users:
    #                 users.add(utuple)

    #                 data2.append(
    #                     {
    #                         "year": accessDate.year,
    #                         "month": accessDate.month - 1,
    #                         "day": accessDate.day,
    #                         "hour": accessDate.hour,
    #                         "user_id": log["user_id"],
    #                         "value": 1,
    #                         "count": 1,
    #                         "teacher":1,
    #                     }
    #                 )

        
    #     for day in period:
    #         if not day in dates_set:
    #             dates_set.add(day)

    #             data2.append(
    #                 {
    #                     "year": day.year,
    #                     "month": day.month - 1,
    #                     "day": day.day,
    #                     "hour": 0,
    #                     "user_id": 0,
    #                     "value": 0,
    #                     "count": 0,
    #                     "teacher":1,
    #                 }
    #             )
        
    # data.extend(data2)
    data = sorted(data, key=lambda x: (x["month"], x["day"]))

    return data

def my_categories(user):
    my_categories = []
    categories = Category.objects.filter() 
    for category in categories:
        if has_category_permissions(user,category) or has:
            my_categories.append(category)
    
    return my_categories

def generalStudentsAccess(subject, dataIni, dataEnd):
    students = subject.students.all()
    professores = subject.professor.all()
    
    if dataIni == "":
        dataIni = "now-30d"

    if dataEnd == "":
        dataEnd = "now"

    data = []
    searchs = []
    cont = 0
    for student in students:
        cont+=1
        searchs.append(
            count_access_subject_period(subject.id, student.id, dataIni, dataEnd)
        )
    for professor in professores:
        searchs.append(
            count_access_subject_period(subject.id, professor.id, dataIni, dataEnd)
        )

    if searchs:
        res = multi_search(searchs)
        

        accessess = [x.to_dict()["hits"]["total"]["value"] for x in res]
        for i, access in enumerate(accessess):
            item = {}
            if i < cont:
                obj = students[i]
                item["teacher"] = 0
            else:
                obj = professores[i-cont]
                item["teacher"] = 1
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

def general_logs(user, data_ini, data_end):
    period = get_days_in_period(data_ini, data_end)
    logs_data = list()
    logs = Log.objects.filter(

    )
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
        searchs.append(count_daily_general_logs_access(day))
        days.append(day)

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()["hits"] for x in res]
        users = set()
        dates_set = set()

        for access in accessess:
            for hits in access["hits"]:
                log = hits["_source"]
                time = parse_datetime(log["datetime"]).strftime('%d/%m/%Y')
                data.append({'x': time, 'y':1})
                # dates_set.add(accessDate.date())
                # utuple = (
                #     str(x.day)
                #     + "-"
                #     + str(x.month)
                #     + "-"
                #     + str(x.year),
                #     log["user_id"],
                # )

                # if not utuple in users:
                #     users.add(utuple)
                    # data.append(
                    #     {
                    #         "year": accessDate.year,
                    #         "month": accessDate.month - 1,
                    #         "day": accessDate.day,
                    #         "user_id": log["user_id"],
                    #         "value": 1,
                    #         "count": 1,
                    #     }
                    # )

        # for day in period:
        #     if not day in dates_set:
        #         dates_set.add(day)

                # data.append(
                #     {
                #         "year": day.year,
                #         "month": day.month - 1,
                #         "day": day.day,
                #         "user_id": 0,
                #         "value": 0,
                #         "count": 0,
                #     }
                # )

        # data = sorted(data, key=lambda x: (x["x"]))
    
    return data

def active_users_qty(request_user,data_ini, data_end):
    logs = list()
    cont=0
    categories = my_categories(request_user)
    subjects = Subject.objects.filter(category__in = categories).order_by('slug').distinct()
    
    total_students = 0
    total_teachers = 0
    ac_students = 0
    ac_teachers= 0
    id_students = []
    id_teachers = []
    all_students = []
    all_teachers = []
    
    for sub in subjects:
        sub=get_object_or_404(Subject, slug = sub.slug)
        students = sub.students.all().values_list("id", flat=True)
        professores = sub.professor.all().values_list("id", flat=True)
        
        for student in students:
            if student not in id_students:
                all_students.append(user_last_interaction_in_period(student, data_ini, data_end))
                id_students.append(student)
                total_students +=1

        for professor in professores:
            if professor not in id_teachers:
                all_teachers.append(user_last_interaction_in_period(professor, data_ini, data_end))
                id_teachers.append(professor)
                total_teachers +=1
                

    res = multi_search(all_students)
    for i, student in enumerate(all_students):
        entry = res[i]
        if entry:
            ac_students+=1
    
    

    res = multi_search(all_teachers)
    for i, professor in enumerate(all_teachers):
        entry = res[i]
        if entry:
            ac_teachers+=1

    data = {
        'total_students': total_students,
        'active_students': ac_students,
        'total_teachers':total_teachers,
        'active_teachers': ac_teachers,
    }
    return data


def functiontable(categories, dataIni, dataEnd):
    data = {}
    categories_data = []
    subjects_data = []
    resources_data = []
    subs = list()
    searchs1 = list()
    searchs2= list()
    searchs3 = list()
    searchs4 = list()
    searchs5 = list()
    searchs6 = list()
    searchs7 = list()
    searchs8 = list()
    for category in categories:
        res = []
        cont=0
        subjects = Subject.objects.filter(category = category).filter(visible = True).order_by('slug').distinct()
        searchs = list()
        accessess =[ ]
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
                cont+=access
                subjects_data.append({
                    'name': obj.name,
                    'access': access,
                    'category': category.name,
                    'link': reverse(
                        "subjects:view",
                        args=(),
                        kwargs={"slug": obj.slug}
                    ),
                })
        categories_data.append({
            'cat_name': category.name,
            'access': cont,
            'link': reverse(
                        "subjects:cat_view",
                        args=(),
                        kwargs={"slug": category.slug}
                    ),
        })
    searchs1.append(
            count_general_resource_logs_period(subs, dataIni, dataEnd)
    )
    if searchs1:
        res1= multi_search(searchs1)
        accessess1 = [x.to_dict()["hits"] for x in res1]
        list_resources = list()
        for i, access in enumerate(accessess1):
            for hits in access["hits"]:
                log = hits["_source"]
                item = {}
                
                resources_data.append({
                        'name': log["resource"],
                        'access': 1,
                        'link': log,
                })
                

   
    data = {
       'categories': categories_data,
       'subjects': subjects_data,
       'resources': resources_data,
    }
    return data

    


