import calendar
import os
from datetime import date, datetime, timedelta
from django.utils import formats, timezone
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.core.urlresolvers import reverse
from django.utils.formats import get_format

from subjects.models import Tag
from topics.models import Resource
from log.models import Log

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

def done_percent(pendency):
    users = get_resource_users(pendency.resource)
    usersDone = PendencyDone.objects.filter(pendency = pendency, student__id__in = users.values_list('id', flat = True)).count()
    
    number_users = users.count()

    done = (usersDone * 100) / number_users

    return done

def get_pend_graph(user, subject):
    pendencies = Pendencies.objects.filter(resource__topic__subject = subject, begin_date__gte = subject.init_date, resource__visible = True)
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
            has_action = PendencyDone.objects.filter(pendency = pendency, student = user)

            item["done"] = has_action.exists()
            item["doneLate"] = False

            if item['done']:
                pDone = has_action.first()

                item["doneLate"] = pDone.late

        graph.append(item)

    return graph

def getAccessedTags(subject, user):
     
    tags = Tag.objects.filter(resource_tags__topic__subject = subject).distinct().all() 

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
            item["details_url"] = reverse('dashboards:tag_accessess', args = (tag.id, subject.slug,user.email), kwargs = {})
            

            if tag.access == 1:
                item["qtd_access"] = res[counter].to_dict()['hits']['total']['value']
                item["qtd_my_access"] = res[counter + 1].to_dict()['hits']['total']['value']
                
                counter = counter + 2
            else:
                item["qtd_access"] = 0
                item["qtd_my_access"] = 0
            data.append(item)
                
    return data

def getAccessedTagsPeriod(subject, user, data_ini='',data_end=''):
    
    tags = Tag.objects.filter(resource_tags__topic__subject = subject).distinct().all() 
    if(data_ini == ""):
        data_ini='now-30d'
    if(data_end== ""):
        data_end='now'
    print(data_ini)
    print(data_end)
    data = []
    searchs = []
    for tag in tags:
        if not tag.name == '':
            resources = Resource.objects.filter(tags__id = tag.id, topic__subject = subject)

            if resources.count() > 0:
                searchs.append(count_logs_period(resources, data_ini, data_end))
                searchs.append(count_logs_period(resources, data_ini, data_end, user.id))
                tag.access = 1
                
            else:
                tag.access = 0

    res = multi_search(searchs)

    counter = 0
    
    for tag in tags:
        if not tag.name == '':
            item = {}
            item["tag_name"] = tag.name
            item["details_url"] = reverse('dashboards:tag_accessess_period', args = (tag.id, subject.slug,user.email, data_ini, data_end), kwargs = {})
            
            

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


def getTagAccessessPeriod(subject, tag, user,data_ini,data_end):
    resources = Resource.objects.filter(tags = tag, topic__subject = subject)
    print(data_ini)
    print(data_end)
    if(data_ini == ""):
        data_ini='now-30d'
    if(data_end== ""):
        data_end='now'
    
    data = []
    searchs = []
    for resource in resources:
        searchs.append(resource_accessess_period(resource,data_ini,data_end))
        searchs.append(resource_accessess_period(resource,data_ini,data_end,user.id))

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
    logs = Log.objects.filter(datetime__date__gte = timezone.now() - timedelta(hours = 7*24+3), datetime__date__lte = timezone.now() - timedelta(hours = 3))

    data = []
    searchs = []

    students = subject.students.all()
    
    #First indicator
    for student in students:
        if student.id != user.id:
            searchs.append(count_access_subject(subject.id, student.id))
            

    searchs.append(count_access_subject(subject.id, user.id))

    item = {}

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()['hits']['total']['value'] for x in res]

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
    else:
        item['percentil_1'] = 0
        item['percentil_2'] = 0
        item['percentil_3'] = 0
        item['percentil_4'] = 0 
        item['max_access'] = 0
        item['my_access'] = 0
    
    data.append(item)
    
    searchs = []

    #Second indicator
    for student in students:
        if student.id != user.id:
            searchs.append(count_diff_days(subject.id, student.id))

    searchs.append(count_diff_days(subject.id, user.id))

    item = {}
    
    if searchs:
        res = multi_search(searchs)
       
        accessess = [len(x.to_dict()['aggregations']['dt']['buckets']) if 'aggregations' in x.to_dict() else 0 for x in res]

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
    else:
        item['percentil_1'] = 0
        item['percentil_2'] = 0
        item['percentil_3'] = 0
        item['percentil_4'] = 0 
        item['max_access'] = 0
        item['my_access'] = 0

    data.append(item)

    searchs = []

    #Third indicator
    for student in students:
        if student.id != user.id:
            searchs.append(count_access_resources(subject.id, student.id))
            
    
    searchs.append(count_access_resources(subject.id, user.id))
    
    item = {}

    if searchs:
        res = multi_search(searchs)
        
        accessess = [x.to_dict()['hits']['total']['value'] for x in res]

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
    else:
        item['percentil_1'] = 0
        item['percentil_2'] = 0
        item['percentil_3'] = 0
        item['percentil_4'] = 0 
        item['max_access'] = 0
        item['my_access'] = 0

    data.append(item)

    #Fourth indicator
    resources_access = logs.filter(component = 'resources', action='view', context__contains = {'subject_id': subject.id})
    
    s = [student.id for student in students]
    accessess=[]

    students_sets = {key: set() for key in s}

    for entry in resources_access.filter(user_id__in = s).all():
        students_sets[entry.user_id].add(entry.context['%s_id'%(entry.resource)])

    students_accessess = [len(students_sets[x]) for x in students_sets]

    students_accessess.sort()
    
    item = {}
    
    if students_accessess:
        my_access = set()

        for entry in resources_access.filter(user_id = user.id).all():
            my_access.add(entry.context['%s_id'%(entry.resource)])

        qtd_results = len(students_accessess)

        if qtd_results > 5:
            item['percentil_1'] = students_accessess[math.floor(qtd_results * 0.25)]
            item['percentil_2'] = students_accessess[math.floor(qtd_results * 0.5)]
            item['percentil_3'] = students_accessess[math.floor(qtd_results * 0.75)]
            item['percentil_4'] = students_accessess[math.floor(qtd_results * 0.9)]
        else:
            item['percentil_1'] = students_accessess[-5] if len(students_accessess) == 5 else 0
            item['percentil_2'] = students_accessess[-4] if len(students_accessess) > 3 else 0
            item['percentil_3'] = students_accessess[-3] if len(students_accessess) > 2 else 0
            item['percentil_4'] = students_accessess[-2] if len(students_accessess) > 1 else 0 

        item['max_access'] = students_accessess[-1]
        item['my_access'] = len(my_access)
    else:
        item['percentil_1'] = 0
        item['percentil_2'] = 0
        item['percentil_3'] = 0
        item['percentil_4'] = 0 
        item['max_access'] = 0
        item['my_access'] = 0

    data.append(item)
        
    #Fifth indicator
    
    pend = Pendencies.objects.filter(resource__topic__subject = subject.id, resource__visible = True, begin_date__date__lt=timezone.now() - timedelta(hours = 3), end_date__date__gte = timezone.now() - timedelta(hours = 7*24+3))
    accessess = []
    
    item = {}

    if pend.count() > 0:
        for student in students:
            if student.id != user.id:
                accessess.append(PendencyDone.objects.filter(pendency__id__in = pend.values_list('id', flat = True), late = False, student = student).count())

        accessess.append(PendencyDone.objects.filter(pendency__id__in = pend.values_list('id', flat = True), late = False, student = user).count())

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
    else:
        item['percentil_1'] = 0
        item['percentil_2'] = 0
        item['percentil_3'] = 0
        item['percentil_4'] = 0 
        item['max_access'] = 0
        item['my_access'] = 0

    data.append(item)
    
    return data

def accessResourceCount(subject, dataIni, dataEnd):
    resources = Resource.objects.filter(topic__subject = subject)
    if dataIni == '':
        dataIni = 'now-30d'
    if dataEnd == '':
        dataEnd = 'now'
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
            item["qtd_access"] = res[counter].to_dict()['hits']['total']['value']
            item["access_url"] = resource.access_link()
            counter = counter + 1
            data.append(item)
        data.sort(key=lambda x: x['qtd_access'], reverse=True)
    return data



def studentsAccess(subject, dataIni, dataEnd):
    students = subject.students.all()

    if dataIni == '':
        dataIni = 'now-30d'

    if dataEnd == '':
        dataEnd = 'now'

    data = []
    searchs = []
    
    for student in students:
        searchs.append(count_access_subject_period(subject.id, student.id, dataIni, dataEnd))

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()['hits']['total']['value'] for x in res]
        

        for i, access in enumerate(accessess):
            item = {}
            
            obj = students[i]

            item['count'] = access
            item['image'] = obj.image_url
            item['user'] = str(obj)
            item['user_id'] = obj.id
            item['link'] = reverse('dashboards:view_subject_student', args = (), kwargs = {"slug": subject.slug, "email": obj.email})

            data.append(item)

        data.sort(key=lambda x: x['count'], reverse=True)

    return data


def parse_date(date_str):
    """Parse date from string by DATE_INPUT_FORMATS of current language"""
    for item in get_format('DATE_INPUT_FORMATS'):
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
        if (data_ini <= day <= data_end):
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
            if (data_ini <= day <= data_end):
                days_set.add(day)

    dates_end = c.itermonthdates(data_end.year, data_end.month)

    for day in dates_end:
        if (data_ini <= day <= data_end):
            days_set.add(day)

    return days_set



def monthly_users_activity(subject, data_ini, data_end):
    period = get_days_in_period(data_ini, data_end)

    students = subject.students.all().values_list('id', flat = True)

    data = list()

    searchs = []
    days = []

    for day in period:
        searchs.append(count_daily_access(subject.id, list(students), day))
        days.append(day)

    if searchs:
        res = multi_search(searchs)

        accessess = [x.to_dict()['hits'] for x in res]

        users = set()
        dates_set = set()

        for access in accessess:
            for hits in access['hits']:
                log = hits['_source']

                accessDate = parse_datetime(log['datetime'])
                dates_set.add(accessDate.date())

                utuple = (str(accessDate.day) + '-' + str(accessDate.month) + '-' + str(accessDate.year), log['user_id'])

                if not utuple in users:
                    users.add(utuple)
                    
                    data.append({'year': accessDate.year, 'month': accessDate.month - 1, 'day': accessDate.day, 'hour': accessDate.hour, 'user_id': log['user_id'], 'value': 1, 'count': 1})

        for day in period:
            if not day in dates_set:
                dates_set.add(day)

                data.append({'year': day.year, 'month': day.month - 1, 'day': day.day, 'hour': 0, 'user_id': 0, 'value': 0, 'count': 0})

        data = sorted(data, key = lambda x: (x['month'], x['day']))

    return data

def get_avatar_audios(subject, user):
    audios = []
    audio_url = os.path.join(settings.MEDIA_URL, 'avatar_audio')
    audiodir = os.path.join(settings.MEDIA_ROOT, 'avatar_audio')

    if not os.path.isdir(audiodir):
        os.makedirs(audiodir)

    tts = gTTS(text = "Olá, %s!"%(str(user)), lang = 'pt-br')
    tts.save(os.path.join(audiodir, 'welcome_%s.mp3'%(str(user))))

    track = MP3(os.path.join(audiodir, 'welcome_%s.mp3'%(str(user))))

    audios.append({ 'file': os.path.join(audio_url, 'welcome_%s.mp3'%(str(user))), 'duration': track.info.length, 'text': "Olá, <b>%s</b>!"%(str(user))})

    logs = Log.objects.filter(datetime__date__gte = subject.init_date, component = 'subject', action = 'view', resource = 'analytics', user_id = user.id, context__contains = {'subject_id': subject.id})

    if not logs.exists():
        tts = gTTS(text = "Seja bem-vindo ao painel de estudante", lang = 'pt-br')
        tts.save(os.path.join(audiodir, 'intro.mp3'))

        track = MP3(os.path.join(audiodir, 'intro.mp3'))

        audios.append({ 'file': os.path.join(audio_url, 'intro.mp3'), 'duration': track.info.length, 'text': "Seja bem-vindo ao painel de estudante"})
        
        tts = gTTS(text = "O painel serve para te manter atento em relação às atividades e recursos da disciplina", lang = 'pt-br')
        tts.save(os.path.join(audiodir, 'definition.mp3'))

        track = MP3(os.path.join(audiodir, 'definition.mp3'))

        audios.append({ 'file': os.path.join(audio_url, 'definition.mp3'), 'duration': track.info.length, 'text': "O painel serve para te manter atento em relação às atividades e recursos da disciplina"})
        
        tts = gTTS(text = "Acesse-o regularmente", lang = 'pt-br')
        tts.save(os.path.join(audiodir, 'warning.mp3'))

        track = MP3(os.path.join(audiodir, 'warning.mp3'))

        audios.append({ 'file': os.path.join(audio_url, 'warning.mp3'), 'duration': track.info.length, 'text': "Acesse-o regularmente"})

    return audios



def avatar_cloud(subject, user):
    audios = []
    audio_url = os.path.join(settings.MEDIA_URL, 'avatar_audio')
    audiodir = os.path.join(settings.MEDIA_ROOT, 'avatar_audio')

    if not os.path.isdir(audiodir):
        os.makedirs(audiodir)
    
    logs = Log.objects.filter(datetime__date__gte = subject.init_date, component = 'subject', action = 'view', resource = 'analytics', user_id = user.id, context__contains = {'subject_id': subject.id})

    if not logs.exists():
        tts = gTTS(text = "Esta é a nuvem de tags", lang = 'pt-br')
        tts.save(os.path.join(audiodir, 'cloud1.mp3'))

        track = MP3(os.path.join(audiodir, 'cloud1.mp3'))

        audios.append({ 'file': os.path.join(audio_url, 'cloud1.mp3'), 'duration': track.info.length, 'text': "Esta é a <b>nuvem de tags</b>"})
        
        tts = gTTS(text = "Através dela é possível identificar os recursos mais populares da disciplina", lang = 'pt-br')
        tts.save(os.path.join(audiodir, 'cloud2.mp3'))

        track = MP3(os.path.join(audiodir, 'cloud2.mp3'))

        audios.append({ 'file': os.path.join(audio_url, 'cloud2.mp3'), 'duration': track.info.length, 'text': "Através dela é possível identificar os recursos mais populares da disciplina"})
        
        tts = gTTS(text = "Quanto maior a palavra, mais a turma acessou", lang = 'pt-br')
        tts.save(os.path.join(audiodir, 'cloud3.mp3'))

        track = MP3(os.path.join(audiodir, 'cloud3.mp3'))

        audios.append({ 'file': os.path.join(audio_url, 'cloud3.mp3'), 'duration': track.info.length, 'text': "Quanto <b>maior</b> a palavra, <b>mais</b> a turma acessou"})
        
        tts = gTTS(text = "Quanto mais clara, mais vezes você acessou em relação à turma", lang = 'pt-br')
        tts.save(os.path.join(audiodir, 'cloud4.mp3'))

        track = MP3(os.path.join(audiodir, 'cloud4.mp3'))

        audios.append({ 'file': os.path.join(audio_url, 'cloud4.mp3'), 'duration': track.info.length, 'text': "Quanto <b>mais clara</b>, <b>mais vezes</b> você acessou em relação à turma"})
        
        subject_url = reverse('subjects:view', args = (subject.slug,), kwargs = {})

        tts = gTTS(text = "Saiba mais em: %s"%(subject_url), lang = 'pt-br')
        tts.save(os.path.join(audiodir, 'cloud5_%s.mp3'%(subject.id)))

        track = MP3(os.path.join(audiodir, 'cloud5_%s.mp3'%(subject.id)))

        audios.append({ 'file': os.path.join(audio_url, 'cloud5_%s.mp3'%(subject.id)), 'duration': track.info.length, 'text': "Saiba mais em: <a href='%s' target='_blank'>%s</a>"%(subject_url,subject_url)})

        return audios

    tags = Tag.objects.filter(resource_tags__topic__subject = subject).distinct().all() 

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
            item["details_url"] = reverse('dashboards:tag_accessess', args = (tag.id, subject.slug,user.email), kwargs = {})
            

            if tag.access == 1:
                item["qtd_access"] = res[counter].to_dict()['hits']['total']['value']
                item["qtd_my_access"] = res[counter + 1].to_dict()['hits']['total']['value']
                
                counter = counter + 2
            else:
                item["qtd_access"] = 0
                item["qtd_my_access"] = 0
            data.append(item)

    data = sorted(data, key = lambda x: x['qtd_access'], reverse = True)
    data = data[0:math.floor(30 / 1000 * 775)]

    most_accessed = data[0]

    if most_accessed['qtd_my_access'] <= 0:
        tts = gTTS(text = "Estes recursos estão em alta, dá uma conferida", lang = 'pt-br')
        tts.save(os.path.join(audiodir, 'most_accessed.mp3'))

        track = MP3(os.path.join(audiodir, 'most_accessed.mp3'))

        audios.append({ 'file': os.path.join(audio_url, 'most_accessed.mp3'), 'duration': track.info.length, 'text': "Estes recursos estão em alta, dá uma conferida", 'resource_link': most_accessed['details_url'], 'tagName': most_accessed['tag_name']})

        return audios

    less_accessed = data[len(data) - 1]

    if less_accessed['qtd_my_access'] <= 0:
        tts = gTTS(text = "Talvez você tenha deixado de ver algo importante", lang = 'pt-br')
        tts.save(os.path.join(audiodir, 'less_accessed.mp3'))

        track = MP3(os.path.join(audiodir, 'less_accessed.mp3'))

        audios.append({ 'file': os.path.join(audio_url, 'less_accessed.mp3'), 'duration': track.info.length, 'text': "Talvez você tenha deixado de ver algo importante", 'resource_link': less_accessed['details_url'], 'tagName': less_accessed['tag_name']})

        return audios

    tts = gTTS(text = "Parabéns! Continue acessando regularmente o ambiente da disciplina", lang = 'pt-br')
    tts.save(os.path.join(audiodir, 'congratulations.mp3'))

    track = MP3(os.path.join(audiodir, 'congratulations.mp3'))

    audios.append({ 'file': os.path.join(audio_url, 'congratulations.mp3'), 'duration': track.info.length, 'text': "Parabéns! Continue acessando regularmente o ambiente da disciplina"})

    return audios