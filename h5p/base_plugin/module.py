""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
##
# Django module h5p.
##
import os
import re
import json
import math
import time
import uuid
import shutil
import hashlib
import collections
from django.conf import settings
from django.contrib.auth.models import User

from h5p.models import *
from .classes import H5PDjango

STYLES = [
    "styles/h5p.css",
    "styles/h5p-confirmation-dialog.css",
    "styles/h5p-core-button.css"
]

OVERRIDE_STYLES = '/static/h5p/styles/h5pp.css'

SCRIPTS = [
    "js/jquery.js",
    "js/h5p.js",
    "js/h5p-event-dispatcher.js",
    "js/h5p-x-api-event.js",
    "js/h5p-x-api.js",
    "js/h5p-content-type.js",
    "js/h5p-confirmation-dialog.js",
    "js/h5p-action-bar.js"
]

##
# Get path to HML5 Package
##


def h5pGetExportPath(content):
    return os.path.join(settings.MEDIA_ROOT, 'h5pp', 'exports', ((content['slug'] + '-') if 'slug' in content else ''), str(content['id']) + '.h5p')

##
# Creates the title for the library details page
##


def h5pLibraryDetailsTitle(libraryId):
    result = h5p_libraries.objects.filter(library_id=libraryId).values('title')
    return result[0] if len(result) > 0 else None

##
# Insert a new content
##


def h5pInsert(request, interface):
    if 'h5p_upload' in request.POST:
        storage = interface.h5pGetInstance('storage')
        storage.savePackage(h5pGetContentId(request), None, False, {
                            'disable': request.POST['disable'], 'title': request.POST['name']})
    else:
        if not 'name' in request.POST['main_library']:
            lib = h5p_libraries.objects.filter(library_id=request.POST['main_library_id']).values(
                'machine_name', 'major_version', 'minor_version')
            lib = {
                'libraryId': request.POST['main_library_id'],
                'machineName': lib.machine_name,
                'majorVersion': lib.major_version,
                'minorVersion': lib.minor_version
            }
        else:
            lib = {
                'libraryId': request.POST['main_library_id'],
                'machineName': request.POST['main_library']['name'] if 'name' in request.POST['main_library'] else '',
                'majorVersion': request.POST['main_library']['majorVersion'] if 'majorVersion' in request.POST['main_library'] else '',
                'minorVersion': request.POST['main_library']['minorVersion'] if 'minorVersion' in request.POST['main_library'] else ''
            }
        core = h5pGetInstance('core')
        core.saveContent({
            'id': h5pGetContentId(request),
            'title': request.POST['title'],
            'params': request.POST['json_content'],
            'embed_type': request.POST['embed_type'],
            'disable': request.POST['disable'],
            'library': lib,
            'author': request.user.username,
            'h5p_library': request.POST['h5p_library'] if 'h5p_library' in request.POST else None
        }, request.POST['nid'])

    return True


def h5pUpdate(request):
    if 'h5p_upload' in request:
        storage = h5pGetInstance('storage')
        storage.savePackage({
            'id': h5pGetContentId(request),
            'title': request.POST['title'],
            'disable': request.POST['disable']
        }, request.POST['nid'], False)
    else:
        h5pInsert(request)


def h5pDelete(request):
    content = h5p_contents.objects.get(content_id=request.GET['contentId'])
    h5pDeleteH5PContent(request, content)

    if 'main_library' in request.POST:
        # Log content delete
        event = H5PEvent('content', 'delete',
                        request.POST['nid'],
                        request.POST['title'],
                        request.POST['main_library']['name'],
                        request.POST['main_library'][
                            'majorVersion'] + '.' + request.POST['main_library']['minorVersion']
                        )

##
# Delete all data related to H5P content
##


def h5pDeleteH5PContent(request, content):
    framework = H5PDjango(request.user)
    storage = framework.h5pGetInstance('storage')
    storage.deletePackage(content)

    # Remove content points
    h5p_points.objects.filter(content_id=content.content_id).delete()

    # Remove content user data
    h5p_content_user_data.objects.filter(
        content_main_id=content.content_id).delete()


def h5pLoad(request):
    interface = H5PDjango(request.user)
    core = interface.h5pGetInstance('core')
    content = core.loadContent(h5pGetContentId(request))
    if content != None:
        request.GET = request.GET.copy()
        request.GET['json_content'] = content['params']
        request.GET['title'] = content['title']
        request.GET['language'] = 'en'
        request.GET['main_library_id'] = content['library']['id']
        request.GET['embed_type'] = content['embed_type']
        request.GET['main_library'] = content['library']
        request.GET['filtered'] = content['filtered']
        request.GET['disable'] = content['disable']
        request.GET['h5p_slug'] = content['slug']


def h5pView(request):
    if not 'in_preview' in request.GET and 'main_library_id' in request.GET:
        html = includeH5p(request)

    if not html:
        html = '<div>' + 'Sorry, preview of H5P content is not yet available.' + '</div>'
    else:
        h5pSetStarted(h5pGetContentId(request))

    return request


def h5pUserDelete(user):
    h5p_points.objects.get(uid=user.id).delete()

    # Remove content user data
    h5p_content_user_data.objects.get(user_id=user.id).delete()

##
# Adds H5P embed code and necessary files
##


def includeH5p(request):
    contentId = h5pGetContentId(request)
    embed = determineEmbedType(request.GET['embed_type'], request.GET['main_library']['embedTypes'])

    data = h5pAddFilesAndSettings(request, embed)
    if embed == 'div':
        html = '<div class="h5p-content" data-content-id="' + contentId + '"></div>'
    else:
        html = '<div class="h5p-iframe-wrapper"><iframe id="h5p-iframe-' + contentId + '" class="h5p-iframe" data-content-id="' + \
            contentId + '" style="height:1px" src="about:blank" frameBorder="0" scrolling="no"></iframe></div>'

    return {'html': html, 'data': data}

##
# Set that the logged in user has started on an h5p
##


def h5pSetStarted(user, contentId):
    if user.id:
        exist = h5p_points.objects.filter(
            content_id=contentId, uid=user.id).values()
        if len(exist) > 0:
            update = h5p_points.objects.get(content_id=contentId, uid=user.id)
            update.content_id = contentId
            update.uid = user.id
            update.started = int(time.time())
            update.save()
        else:
            h5p_points.objects.create(
                content_id=contentId, uid=user.id, started=int(time.time()))

##
# Handle grades storage for users
##


def h5pSetFinished(request):
    # Content parameters
    contentId = request.POST['contentId']
    score = request.POST['score']
    maxScore = request.POST['maxScore']
    response = {
        'success': False
    }

    if contentId.isdigit() and score.isdigit() and maxScore.isdigit():
        update = h5p_points.objects.get(
            content_id=contentId, uid=request.user.id)
        update.finished = int(time.time())
        update.points = score
        update.max_points = maxScore
        update.save()
        response['success'] = True

    return json.dumps(response)

##
# Adds content independent scripts, styles and settings
##


def h5pAddCoreAssets():
    path = 'h5p/'
    assets = {
        'css': list(),
        'js': list()
    }

    for style in STYLES:
        css = path + style
        assets['css'].append(css)

    for script in SCRIPTS:
        js = path + script
        assets['js'].append(js)

    return assets

##
# H5PIntegration object
##


def h5pGetCoreSettings(user):
    coreSettings = {
        'baseUrl': settings.BASE_URL,
        'url': settings.BASE_URL + settings.MEDIA_URL + 'h5pp',
        'postUserStatistics': user.id > 0,
        'ajaxPath': settings.BASE_URL + settings.H5P_URL + 'ajax',
        'ajax': {
            'setFinished': settings.BASE_URL + settings.H5P_URL + 'finishContent/',
            'contentUserData': settings.BASE_URL + settings.H5P_URL + 'ajax/?content-user-data&contentId=:contentId&dataType=:dataType&subContentId=:subContentId'
        },
        'tokens': {
            'result': createToken('result'),
            'contentUserData': createToken('contentuserdata')
        },
        'saveFreq': settings.H5P_SAVE if settings.H5P_SAVE != 0 else 'false',
        'l10n': {
            'H5P': {
                'fullscreen': 'Fullscreen',
                'disableFullscreen': 'Disable fullscreen',
                'download': 'Download',
                'copyrights': 'Rights of use',
                'embed': 'Embed',
                'size': 'Size',
                            'showAdvanced': 'Show advanced',
                            'hideAdvanced': 'Hide advanced',
                            'advancedHelp': 'Include this script on your website if you want dynamic sizing of the embedded content:',
                            'copyrightInformation': 'Rights of use',
                            'close': 'Close',
                            'title': 'Title',
                            'author': 'Author',
                            'year': 'Year',
                            'source': 'Source',
                            'license': 'License',
                            'thumbnail': 'Thumbnail',
                            'noCopyrights': 'No copyright information available for this content.',
                            'downloadDescription': 'Download this content as a H5P file.',
                            'copyrightsDescription': 'View copyright information for this content.',
                            'embedDescription': 'View the embed code for this content.',
                            'h5pDescription': 'Visit H5P.org to check out more cool content.',
                            'contentChanged': 'This content has changed since you last used it.',
                            'startingOver': 'You\'ll be starting over',
                            'by': 'by',
                            'showMore': 'Show more',
                            'showLess': 'Show less',
                            'subLevel': 'Sublevel',
                            'confirmDialogHeader': 'Confirm action',
                            'confirmDialogBody': 'Please confirm that you wish to proceed. This action is not reversible.',
                            'cancelLabel': 'Cancel',
                            'confirmLabel': 'Confirm'
            }
        }
    }

    if user.id:
        coreSettings['user'] = {
            'name': user.username,
            'mail': user.email
        }

    return coreSettings

##
# Adds h5p files and settings
##


def h5pAddFilesAndSettings(request, embedType):
    interface = H5PDjango(request.user)
    integration = h5pGetCoreSettings(request.user)
    assets = h5pAddCoreAssets()

    if not 'json_content' in request.GET or not 'contentId' in request.GET:
        return integration

    content = h5pGetContent(request)
    if 'contents' in integration and content['id'] in integration['contents']:
        return integration

    integration['contents'] = dict()
    integration['contents'][
        str('cid-' + content['id'])] = h5pGetContentSettings(request.user, content)

    core = interface.h5pGetInstance('core')
    preloadedDependencies = core.loadContentDependencies(content['id'])
    files = core.getDependenciesFiles(preloadedDependencies)
    libraryList = h5pDependenciesToLibraryList(preloadedDependencies)

    filesAssets = {
        'js': list(),
        'css': list()
    }
    print(embedType)
    if embedType == 'div':
        for script in files['scripts']:
            url = settings.MEDIA_URL + 'h5pp/' + \
                script['path'] + script['version']
            filesAssets['js'].append(
                settings.MEDIA_URL + 'h5pp/' + script['path'])
            integration['loadedJs'] = url
        for style in files['styles']:
            url = settings.MEDIA_URL + 'h5pp/' + \
                style['path'] + style['version']
            filesAssets['css'].append(
                settings.MEDIA_URL + 'h5pp/' + style['path'])
            integration['loadedCss'] = url
        #Override CSS
        filesAssets['css'].append(OVERRIDE_STYLES)
        integration['loadedCss'] = OVERRIDE_STYLES

    elif embedType == 'iframe':
        h5pAddIframeAssets(request, integration, content['id'], files)
    print(filesAssets['js'])
    return {'integration': json.dumps(integration), 'assets': assets, 'filesAssets': filesAssets}

##
# Get a content by request
##


def h5pGetContent(request):
    interface = H5PDjango(request.user)
    core = interface.h5pGetInstance('core')
    return {
        'id': h5pGetContentId(request),
        'title': request.GET['title'],
        'params': request.GET['json_content'],
        'language': request.GET['language'],
        'library': request.GET['main_library'],
        'embedType': 'div',
        'filtered': request.GET['filtered'],
        'url': settings.BASE_URL + settings.MEDIA_URL + 'h5pp/content/' + h5pGetContentId(request),
        'displayOptions': '',
        'slug': request.GET['h5p_slug']
    }


def h5pGetContentSettings(user, content):
    interface = H5PDjango(user)
    core = interface.h5pGetInstance('core')
    filtered = core.filterParameters(content)

    # Get preloaded user data
    results = h5p_content_user_data.objects.filter(user_id=user.id, content_main_id=content[
                                                'id'], preloaded=1).values('sub_content_id', 'data_id', 'data')

    contentUserData = {
        0: {
            'state': '{}'
        }
    }
    for result in results:
        contentUserData[result['sub_content_id']][
            result['data_id']] = result['data']

    contentSettings = {
        'library': libraryToString(content['library']),
        'jsonContent': filtered,
        'fullScreen': content['library']['fullscreen'],
        'exportUrl': h5pGetExportPath(content),
        'embedCode': str('<iframe src="' + settings.BASE_URL + settings.H5P_URL + 'embed/' + content['id'] + '" width=":w" height=":h" frameborder="0" allowFullscreen="allowfullscreen"></iframe>'),
        'mainId': content['id'],
        'url': str(content['url']),
        'title': str(content['title'].encode('utf-8')),
        'contentUserData': contentUserData,
        'displayOptions': content['displayOptions']
    }
    return contentSettings


def h5pGetResizeUrl():
    return settings.H5P_PATH + '/js/h5p-resizer.js'


def h5pGetContentId(request):
    if not 'contentId' in request.GET:
        return None

    return request.GET['contentId']


def h5pGetListContent(request):
    interface = H5PDjango(request.user)
    contents = interface.getNumContentPlus()
    if contents > 0:
        result = list()
        for content in interface.loadAllContents():
            load = interface.loadContent(content['content_id'])
            load['score'] = getUserScore(content['content_id'])
            result.append(load)
        return result
    else:
        return 0

##
# Determine the correct embed type to use.
##


def determineEmbedType(contentEmbedType, libraryEmbedTypes):
    # Detect content embed type
    embedType = "div" if (
        "div" in contentEmbedType.lower()) else "iframe"

    if libraryEmbedTypes != None and libraryEmbedTypes != "":
        # Check that embed type is available for library
        embedTypes = libraryEmbedTypes.lower()
        if not embedType in embedTypes:
            # Not available, pick default.
            embedType = "div" if "div" in embedTypes else "iframe"

    return embedType

##
# Get a list of libraries more suitable for inspection than the dependencies list
##


def h5pDependenciesToLibraryList(dependencies):
    libraryList = dict()
    for key, dependency in dependencies.items():
        libraryList[dependency['machine_name']] = {
            'majorVersion': dependency['major_version'],
            'minorVersion': dependency['minor_version']
        }
    return libraryList

##
# Add the necessary assets for content to run in an iframe
##


def h5pAddIframeAssets(request, integration, contentId, files):
    framework = H5PDjango(request.user)
    core = framework.h5pGetInstance('core')

    assets = h5pAddCoreAssets()
    integration['core'] = dict()
    integration['core']['scripts'] = assets['js']
    integration['core']['styles'] = assets['css']

    writable = False # Temporary, future feature
    if writable:
        if not os.path.exists(os.path.join(settings.H5P_PATH, 'files')):
            os.mkdir(os.path.join(settings.H5P_PATH, 'files'))

        styles = list()
        externalStyles = list()
        for style in files['styles']:
            if h5pIsExternalAsset(style['path']):
                externalStyles.append(style)
            else:
                styles.append({
                    'data': style['path'],
                    'type': 'file'
                })
        integration['contents'][
            'cid-' + contentId]['styles'] = core.getAssetsUrls(externalStyles)
        integration['contents']['cid-' + contentId]['styles'].append(styles)
    else:
        integration['contents'][
            'cid-' + contentId]['styles'] = core.getAssetsUrls(files['styles'])
        #Override Css
        integration['contents']['cid-' + contentId]['styles'].append(OVERRIDE_STYLES)

    if writable:
        if not os.path.exists(os.path.join(settings.H5P_PATH, 'files')):
            os.mkdir(os.path.join(settings.H5P_PATH, 'files'))

        scripts = dict()
        externalScripts = dict()
        for script in files['scripts']:
            if h5pIsExternalAsset(script['path']):
                externalScripts.append(script)
            else:
                scripts[script['path']] = list()
                scripts[script['path']].append({
                    'data': script['path'],
                    'type': 'file',
                    'preprocess': True
                })
        integration['contents'][
            'cid-' + contentId]['scripts'] = core.getAssetsUrls(externalScripts)
        integration['contents']['cid-' + contentId]['scripts'].append(scripts)
    else:
        integration['contents'][
            'cid-' + contentId]['scripts'] = core.getAssetsUrls(files['scripts'])

##
# Generate embed page to be included in iframe
##
def h5pEmbed(request):
    h5pPath = settings.STATIC_URL + 'h5p/'
    coreSettings = h5pGetCoreSettings(request.user)
    framework = H5PDjango(request.user)
    
    scripts = list()
    for script in SCRIPTS:
        scripts.append(h5pPath + script)
    styles = list()
    for style in STYLES:
        styles.append(h5pPath + style)

    integration = h5pGetCoreSettings(request.user)
    
    content = h5pGetContent(request)

    integration['contents'] = dict()
    integration['contents']['cid-' + content['id']] = h5pGetContentSettings(request.user, content)

    core = framework.h5pGetInstance('core')
    preloadedDependencies = core.loadContentDependencies(content['id'])
    files = core.getDependenciesFiles(preloadedDependencies)
    libraryList = h5pDependenciesToLibraryList(preloadedDependencies)

    scripts = scripts + core.getAssetsUrls(files['scripts'])
    styles = styles + core.getAssetsUrls(files['styles'])

    return {'h5p': json.dumps(integration), 'scripts': scripts, 'styles': styles, 'lang': settings.H5P_LANGUAGE}

def getUserScore(contentId, user=None, ajax=False):
    if user != None:
        scores = h5p_points.objects.filter(
            content_id=contentId, uid=user.id).values('points', 'max_points')
    else:
        scores = h5p_points.objects.filter(content_id=contentId)
        for score in scores:
            score.uid = User.objects.get(id=score.uid).username
            score.has_finished = score.finished >= score.started
            score.points = '..' if score.points == None else score.points
            score.max_points = '..' if score.max_points == None else score.max_points

    if len(scores) > 0:
        if ajax:
            return json.dumps(list(scores))
        return scores

    return None

def exportScore(contentId=None):
    response = ''
    if contentId:
        scores = h5p_points.objects.filter(content_id=contentId)
        content = h5p_contents.objects.get(content_id=contentId)
        response = response + '[Content] : %s - [Users] : %s\n' % (content.title, len(scores))
        for score in scores:
            score.uid = User.objects.get(id=score.uid).username
            score.has_finished = 'Completed' if score.finished >= score.started else 'Not completed'
            score.points = '..' if score.points == None else score.points
            score.max_points = '..' if score.max_points == None else score.max_points
            response = response + '[Username] : %s | [Current] : %s | [Max] : %s | [Progression] : %s\n' % (score.uid, score.points, score.max_points, score.has_finished)
        return response

    scores = h5p_points.objects.all()
    response = response + '[Users] : %s\n' % len(scores)
    currentContent = ''
    for score in scores:
        content = h5p_contents.objects.get(content_id=score.content_id)
        if content.content_id != currentContent:
            response = response + '--------------------\n[Content] : %s\n--------------------\n' % content.title
        score.uid = User.objects.get(id=score.uid).username
        score.has_finished = 'Completed' if score.finished >= score.started else 'Not completed'
        score.points = '..' if score.points == None else score.points
        score.max_points = '..' if score.max_points == None else score.max_points
        response = response + '[Username] : %s | [Current] : %s | [Max] : %s | [Progression] : %s\n' % (score.uid, score.points, score.max_points, score.has_finished)
        currentContent = content.content_id
    return response
##
# Uninstall H5P
##


def uninstall():
    basepath = settings.MEDIA_ROOT + '/h5pp'
    if os.path.exists(basepath):
        shutil.rmtree(basepath)

    h5p_contents_libraries.objects.all().delete()
    h5p_libraries.objects.all().delete()
    h5p_libraries_libraries.objects.all().delete()
    h5p_libraries_languages.objects.all().delete()
    h5p_contents.objects.all().delete()
    h5p_points.objects.all().delete()
    h5p_content_user_data.objects.all().delete()
    h5p_events.objects.all().delete()
    h5p_counters.objects.all().delete()

    return 'H5PP is now uninstalled. Don\'t forget to clean your settings.py and run "pip uninstall H5PP".'

##
# Get a new H5P security token for the given action
##


def createToken(action):
    timeFactor = getTimeFactor()
    h = hashlib.new('md5')
    h.update((action + str(timeFactor) + str(uuid.uuid1())).encode('utf-8'))
    return h.hexdigest()

##
# Create a time based number which is unique for each 12 hour.
##


def getTimeFactor():
    return math.ceil(int(time.time()) / (86400 / 2))

##
# Checks to see if the path is external
##


def h5pIsExternalAsset(path):
    return True if re.search('(?i)^[a-z0-9]+:\/\/', path) else False

##
# Writes library data as string on the form {machineName} {majorVersion}.{minorVersion}
##


def libraryToString(library, folderName=False):
    return str(library["machineName"] if 'machineName' in library else library['name'] + ("-" if folderName else " ") + str(library["majorVersion"]) + "." + str(library["minorVersion"]))

##
# Returns all rows from a cursor as a dict
##
def dictfetchall(self, cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
