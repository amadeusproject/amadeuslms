""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
import os
import re
import json
import time
import django
import requests
import collections
from django.conf import settings
from django.contrib import messages
from django.db import connection
from django.template.defaultfilters import slugify

from h5p.models import *
from .event import H5PEvent
from .library.classes import *
from .editor.editorclasses import H5PDjangoEditor
from .editor.library.editorstorage import H5PEditorStorage


class H5PDjango:
    global path, dirpath, h5pWhitelist, h5pWhitelistExtras
    path = None
    dirpath = None
    h5pWhitelist = 'json png jpg jpeg gif bmp tif tiff svg eot ttf woff woff2 otf webm mp4 ogg mp3 txt pdf rtf doc docx xls xlsx ppt pptx odt ods odp xml csv diff patch swf md textile'
    h5pWhitelistExtras = ' js css'

    def __init__(self, user):
        self.user = user

    ##
    # Get an instance of one of the h5p library classes
    ##
    def h5pGetInstance(self, typ, h5pdir=None, h5p=None):
        if not hasattr(self, 'interface'):
            self.interface = H5PDjango(self.user)

        if h5pdir != None and h5p != None:
            self.interface.getUploadedH5pFolderPath(h5pdir)
            self.interface.getUploadedH5pPath(h5p)

        if not hasattr(self, 'core'):
            self.core = H5PCore(self.interface, os.path.join(settings.MEDIA_ROOT, 'h5pp'), settings.BASE_DIR,
                                'en', True if getattr(settings, 'H5P_EXPORT') else False, False)

        if typ == 'validator':
            return H5PValidator(self.interface, self.core)
        elif typ == 'storage':
            return H5PStorage(self.interface, self.core)
        elif typ == 'contentvalidator':
            return H5PContentValidator(self.interface, self.core)
        elif typ == 'export':
            return H5PExport(self.interface, self.core)
        elif typ == 'interface':
            return self.interface
        elif typ == 'core':
            return self.core
        elif typ == 'editor':
            storage = H5PEditorStorage()
            return H5PDjangoEditor(self.core, storage, settings.BASE_DIR, os.path.join(settings.MEDIA_ROOT, 'h5pp'))

    ##
    # Returns info for the current platform
    ##
    def getPlatformInfo(self):
        h5pInfo = settings.H5P_VERSION

        return {
            'name': 'django',
            'version': django.get_version(),
            'h5pVersion': '7.x'
        }
    ##
    # Fetches a file from a remote server using HTTP GET
    ##

    def fetchExternalData(self, url, data=None):
        if data != None:
            response = requests.post(url, data)
        else:
            response = requests.get(url)

        return response.content if response.status_code == 200 else response.raise_for_status()

    ##
    # Set the tutorial URL for a library. All versions of the library is set
    ##
    def setLibraryTutorialUrl(self, machineName, tutorialUrl):
        tutorial = h5p_libraries.objects.get(machine_name=machineName)
        tutorial.tutorial_url = tutorialUrl
        tutorial.save()

    ##
    # Show the user an error message
    ##
    def setErrorMessage(self, request, message):
        messages.error(request, message)

    ##
    # Show the user an information message
    def setInfoMessage(self, request, message):
        messages.info(request, message)

    ##
    # Get the path to the last uploaded h5p dir
    ##
    def getUploadedH5pFolderPath(self, folder=None):
        global dirpath
        if folder != None:
            dirpath = folder
        return dirpath

    ##
    # Get the path to the last uploaded h5p file
    ##
    def getUploadedH5pPath(self, files=None):
        global path
        if files != None:
            path = files
        return path

    ##
    # Get a list of the current installed libraries
    ##
    def loadLibraries(self):
        result = h5p_libraries.objects.extra(select={'id': 'library_id', 'name': 'machine_name'}).values(
            'id', 'machine_name', 'title', 'major_version', 'minor_version', 'patch_version', 'runnable', 'restricted').order_by('title', 'major_version', 'minor_version')
        if result.exists():
            libraries = dict()
            for library in result:
                libraries[library['machine_name']] = library
            return libraries
        else:
            return ''

    ##
    # Returns the URL to the library admin page
    ##
    def getAdminUrl(self):
        # TODO
        return ''

    ##
    # Get id to an existing library
    # If version number is not specified, the newest version will be returned
    ##
    def getLibraryId(self, machineName, majorVersion=None, minorVersion=None):
        if majorVersion == None or minorVersion == None:
            libraryId = h5p_libraries.objects.filter(
                machine_name=machineName).values('library_id')
        else:
            libraryId = h5p_libraries.objects.filter(
                machine_name=machineName, major_version=majorVersion, minor_version=minorVersion).values('library_id')

        return libraryId[0]['library_id'] if len(libraryId) > 0 and 'library_id' in libraryId[0] else None

    ##
    # Is the library a patched version of an existing library ?
    ##
    def isPatchedLibrary(self, library):
        if self.isInDevMode():
            result = h5p_libraries.objects.filter(machine_name=library['machineName'], major_version=library[
                                                'majorVersion'], minor_version=library['minorVersion'], patch_version__lte=library['patchVersion'])
        else:
            result = h5p_libraries.objects.filter(machine_name=library['machineName'], major_version=library[
                                                'majorVersion'], minor_version=library['minorVersion'], patch_version__lt=library['patchVersion'])

        return result.exists()

    ##
    # Is H5P in development mode ?
    ##
    def isInDevMode(self):
        return bool(settings.H5P_DEV_MODE)

    ##
    # Is the current user allowed to update libraries ?
    ##
    def mayUpdateLibraries(self):
        # TODO
        return True

    ##
    # Get number of content using a library, and the number of
    # dependencies to other libraries
    ##
    def getLibraryUsage(self, libraryId, skipContent=False):
        usage = dict()
        cursor = connection.cursor()
        cursor.execute("""
			SELECT COUNT(distinct n.content_id)
			FROM h5p_libraries l
			JOIN h5p_contents_libraries cl ON l.library_id = cl.library_id
			JOIN h5p_contents n ON cl.content_id = n.content_id
			WHERE l.library_id = %s
		""" % libraryId)
        usage['content'] = cursor.fetchall()
        usage['libraries'] = h5p_libraries_libraries.objects.filter(
            required_library_id=libraryId).count()

        return usage

    ##
    # Get a key value list of library version and count of content created
    # using that library
    ##
    def getLibraryContentCount(self):
        cursor = connection.cursor()
        cursor.execute("""
			SELECT machine_name, major_version, minor_version, count(*) AS count
			FROM h5p_contents, h5p_libraries
			WHERE main_library_id = library_id
			GROUP BY machine_name, major_version, minor_version
		""")
        result = self.dictfetchall(cursor)

        # Extract results
        contentCount = dict()
        for lib in result:
            contentCount[lib['machine_name'] + ' ' +
                        str(lib['major_version']) + '.' + str(lib['minor_version'])] = lib['count']

        return contentCount

    ##
    # Generates statistics from the event log per library
    ##
    def getLibraryStats(self, typ):
        results = h5p_counters.objects.filter(type=typ).extra(
            select={'name': 'library_name', 'version': 'library_version'}).values('name', 'version')

        if results.exists():
            for library in results:
                count[library.name + ' ' + library.version] = library.num
            return count

        return ''

    ##
    # Aggregate the current number of H5P authors
    ##
    def getNumAuthors(self):
        return ''

    ##
    # Store data about a library
    # Also fills in the libraryId in the libraryData object if the object is new
    ##
    def saveLibraryData(self, libraryData, new=True):
        preloadedJs = self.pathsToCsv(libraryData, 'preloadedJs')
        preloadedCss = self.pathsToCsv(libraryData, 'preloadedCss')
        dropLibraryCss = ''

        if 'dropLibraryCss' in libraryData:
            for lib in libraryData['dropLibraryCss']:
                libs.append(lib['machineName'])
            dropLibraryCss = libs.split(', ')

        embedTypes = ''
        if 'embedTypes' in libraryData:
            embedTypes = libraryData['embedTypes']

            if not 'div' in embedTypes and isinstance(embedTypes, list):
                embedTypes.append('div')
        if not 'semantics' in libraryData:
            libraryData['semantics'] = ''
        if not 'fullscreen' in libraryData:
            libraryData['fullscreen'] = 0
        if new:
            libraryId = h5p_libraries.objects.create(
                machine_name=libraryData['machineName'],
                title=libraryData['title'],
                major_version=libraryData['majorVersion'],
                minor_version=libraryData['minorVersion'],
                patch_version=libraryData['patchVersion'],
                runnable=libraryData['runnable'],
                fullscreen=libraryData['fullscreen'],
                embed_types=embedTypes,
                preloaded_js=preloadedJs,
                preloaded_css=preloadedCss,
                drop_library_css=dropLibraryCss,
                semantics=libraryData['semantics'])
            libraryData['libraryId'] = libraryId.library_id
        else:
            library = h5p_libraries.objects.get(library_id=libraryData['libraryId'])
            library.title = libraryData['title']
            library.patch_version = libraryData['patchVersion']
            library.runnable = libraryData['runnable']
            library.fullscreen = libraryData['fullscreen']
            library.embed_types = embedTypes
            library.preloaded_js = preloadedJs
            library.preloaded_css = preloadedCss
            library.drop_library_css = dropLibraryCss
            library.semantics = libraryData['semantics']
            library.save()

            self.deleteLibraryDependencies(libraryData['libraryId'])

        # Log library, installed or updated
        event = H5PEvent(self.user, 'library', ('create' if new else 'update'), None, None, libraryData[
                        'machineName'], str(libraryData['majorVersion']) + '.' + str(libraryData['minorVersion']))

        h5p_libraries_languages.objects.filter(
            library_id=libraryData['libraryId']).delete()
        if 'language' in libraryData:
            for languageCode, languageJson in libraryData['language'].items():
                pid = h5p_libraries_languages.objects.create(library_id=libraryData['libraryId'], language_code=languageCode, language_json=languageJson)

    ##
    # Convert list of file paths to csv
    ##
    def pathsToCsv(self, libraryData, key):
        if key in libraryData:
            paths = list()
            for f in libraryData[key]:
                paths.append(f['path'])
            return paths
        return ''

    ##
    # Delete all dependencies belonging to given library
    ##
    def deleteLibraryDependencies(self, libraryId):
        if h5p_libraries_libraries.objects.filter(library_id=libraryId).count() > 0:
            h5p_libraries_libraries.objects.get(library_id=libraryId).delete()

    ##
    # Delete a library from database and file system
    ##
    def deleteLibrary(self, libraryId):
        library = h5p_libraries.objects.get(library_id=libraryId)

        # Delete files
        self.deleteFileTree(os.path.join(settings.MEDIA_ROOT, 'h5pp', 'libraries',
                                        library.machine_name + '-' + library.major_version + '.' + library.minor_version))

        # Delete data in database (won't delete content)
        h5p_libraries_libraries.objects.get(library_id=libraryId).delete()
        h5p_libraries_languages.objects.get(library_id=libraryId).delete()
        h5p_libraries.objects.get(library_id=libraryId).delete()

    ##
    # Save what libraries a library is depending on
    ##
    def saveLibraryDependencies(self, libraryId, dependencies, dependencyType):
        for dependency in dependencies:
            pid = h5p_libraries.objects.filter(machine_name=dependency['machineName'], major_version=dependency[
                                            'majorVersion'], minor_version=dependency['minorVersion']).values('library_id')[0]
            h5p_libraries_libraries.objects.create(library_id=libraryId, required_library_id=pid[
                                                'library_id'], dependency_type="'" + dependencyType + "'")

    ##
    # Update old content
    ##
    def updateContent(self, content, contentMainId=None):
        contentId = h5p_contents.objects.filter(
            content_id=content['id']).values('content_id')
        if not contentId.exists():
            self.insertContent(content, contentMainId)
            return

        # Update content
        update = h5p_contents.objects.get(content_id=contentId)
        update.title = content['title']
        update.author = content['author']
        update.json_contents = content['params']
        update.embed_type = 'div'
        update.main_library_id = content['library']['libraryId']
        update.filtered = ''
        update.disable = content['disable']
        update.slug = slugify(content['title'])
        update.save()

        # Derive library data from string
        if 'h5p_library' in content:
            libraryData = content['h5p_library'].split(' ')
            content['library']['machineName'] = libraryData[0]
            content['machineName'] = libraryData[0]
            libraryVersions = libraryData[1].split('.')
            content['library']['majorVersion'] = libraryVersions[0]
            content['library']['minorVersion'] = libraryVersions[1]

        # Log update event
        event = H5PEvent('content', 'update', content['id'], content['title'], content['library'][
                        'machineName'], str(content['library']['majorVersion']) + '.' + str(content['library']['minorVersion']))

    ##
    # Insert new content
    ##
    def insertContent(self, content, contentMainId=None):
        # Insert
        result = h5p_contents.objects.create(
            title=content['title'],
            json_contents=content['params'],
            embed_type='div',
            content_type=content['library']['machineName'],
            main_library_id=content['library']['libraryId'],
            author=content['author'],
            disable=content['disable'],
            filtered='',
            slug=slugify(content['title']))

        event = H5PEvent('content', 'create', result.content_id, content['title'] if 'title' in content else '', content[
                        'library']['machineName'], str(content['library']['majorVersion']) + '.' + str(content['library']['minorVersion']))

        return result.content_id

    ##
    # Resets marked user data for the given content
    ##
    def resetContentUserData(self, contentId):
        if h5p_content_user_data.objects.filter(content_main_id=contentId, delete_on_content_change=1).count() > 0:
            # Reset user datas for this content
            userData = h5p_content_user_data.objects.filter(
                content_main_id=contentId, delete_on_content_change=1)
            for user in userData:
                user.timestamp = int(time.time())
                user.data = 'RESET'
                user.save()
    ##
    # Get file extension whitelist
    # The default extension list is part of h5p, but admins should be allowed to modify it
    ##

    def getWhitelist(self, isLibrary, defaultContentWhitelist, defaultLibraryWhitelist):
        global h5pWhitelist, h5pWhitelistExtras
        whitelist = h5pWhitelist
        if isLibrary:
            whitelist = whitelist + h5pWhitelistExtras
        return whitelist

    ##
    # Give an H5P the same library dependencies as a given H5P
    ##
    def copyLibraryUsage(self, contentId, copyFromId, contentMainId=None):
        copy = h5p_contents_libraries.objects.get(content_id=copyFromId)
        h5p_contents_libraries.objects.filter(content_id=copyFromId).create(
            content_id=contentId, library_id=copy.library_id, dependency_type=copy.dependency_type, drop_css=copy.drop_css, weight=copy.weight)

    ##
    # Deletes content data
    ##
    def deleteContentData(self, contentId):
        h5p_contents.objects.get(content_id=contentId).delete()
        self.deleteLibraryUsage(contentId)

    ##
    # Delete what libraries a content item is using
    ##
    def deleteLibraryUsage(self, contentId):
        h5p_contents_libraries.objects.filter(content_id=contentId).delete()

    ##
    # Saves what libraries the content uses
    ##
    def saveLibraryUsage(self, contentId, librariesInUse):
        dropLibraryCssList = dict()
        for key, dependency in librariesInUse.items():
            if 'dropLibraryCss' in dependency['library']:
                dropLibraryCssList = dropLibraryCssList + \
                    dependency['library']['drop_library_css'].split(', ')

        for key, dependency in librariesInUse.items():
            dropCss = 1 if dependency['library'][
                'machine_name'] in dropLibraryCssList else 0
            h5p_contents_libraries.objects.create(
                content_id=contentId,
                library_id=dependency['library']['library_id'],
                dependency_type=dependency['type'],
                drop_css=dropCss,
                weight=dependency['weight'])

    ##
    # Load a library
    ##
    def loadLibrary(self, machineName, majorVersion, minorVersion):
        library = h5p_libraries.objects.filter(
            machine_name=machineName, major_version=majorVersion, minor_version=minorVersion).defer('restricted').values()

        if not library.exists():
            return False

        library = library[0]

        cursor = connection.cursor()
        cursor.execute("""
			SELECT hl.machine_name AS name,
					hl.major_version AS major,
					hl.minor_version AS minor,
					hll.dependency_type AS type
			FROM h5p_libraries_libraries hll
			JOIN h5p_libraries hl ON hll.required_library_id = hl.library_id
			WHERE hll.library_id = %s
		""" % library['library_id'])
        result = self.dictfetchall(cursor)

        for dependency in result:
            typ = dependency['type'].replace("'", "") + 'Dependencies'
            if not typ in library:
                library[typ] = list()
            library[typ].append({
                'machineName': dependency['name'],
                'majorVersion': dependency['major'],
                'minorVersion': dependency['minor']
            })
        if self.isInDevMode():
            semantics = self.getSemanticsFromFile(library['machine_name'], library['major_version'], library['minor_version'])
            if semantics:
                library['semantics'] = semantics

        return library

    def getSemanticsFromFile(self, machineName, majorVersion, minorVersion):
        semanticsPath = os.path.join(settings.H5P_PATH, 'libraries', machineName + '-' +
                                    str(majorVersion) + '.' + str(minorVersion), 'semantics.json')
        if os.path.exists(semanticsPath):
            semantics = semanticsPath.read()
            if not json.loads(semantics):
                print('Invalid json in semantics for %s' %library['machineName'])
            return semantics
        return False

    ##
    # Loads library semantics
    ##
    def loadLibrarySemantics(self, machineName, majorVersion, minorVersion):
        if self.isInDevMode():
            semantics = self.getSemanticsFromFile(
                machineName, majorVersion, minorVersion)
        else:
            semantics = h5p_libraries.objects.filter(
                machine_name=machineName, major_version=majorVersion, minor_version=minorVersion).values('semantics')

        return None if len(semantics) == 0 else semantics[0]

    ##
    # Make it possible to alter the semantics, adding custom fields, etc.
    ##
    def alterLibrarySemantics(self, semantics, name, majorVersion, minorVersion):
        # TODO
        return ''

    ##
    # Load content
    ##
    def loadContent(self, pid):
        cursor = connection.cursor()
        cursor.execute("""
			SELECT hn.content_id AS id,
					hn.title,
					hn.json_contents AS params,
					hn.embed_type,
                    hn.content_type,
                    hn.author,
					hl.library_id,
					hl.machine_name AS library_name,
					hl.major_version AS library_major_version,
					hl.minor_version AS library_minor_version,
					hl.embed_types AS library_embed_types,
					hl.fullscreen AS library_fullscreen,
					hn.filtered,
					hn.disable,
					hn.slug
			FROM h5p_contents hn
			JOIN h5p_libraries hl ON hl.library_id = hn.main_library_id
			WHERE content_id = %s
		""" % pid)
        content = self.dictfetchall(cursor)
        return None if len(content) == 0 else content[0]

    ##
    # Load all contents available
    ##
    def loadAllContents(self):
        result = h5p_contents.objects.values('content_id', 'title')
        return result if len(result) > 0 else None

    ##
    # Load dependencies for the given content of the given type
    ##
    def loadContentDependencies(self, pid, typ=None):
        cursor = connection.cursor()
        if typ != None:
            cursor.execute("""
				SELECT hl.library_id,
						hl.machine_name,
						hl.major_version,
						hl.minor_version,
						hl.patch_version,
						hl.preloaded_css,
						hl.preloaded_js,
						hnl.drop_css,
						hnl.dependency_type
				FROM h5p_contents_libraries hnl
				JOIN h5p_libraries hl ON hnl.library_id = hl.library_id
				WHERE hnl.content_id = %s AND hnl.dependency_type = %s
				ORDER BY hnl.weight
			""" % (pid, "'" + typ + "'"))
        else:
            cursor.execute("""
				SELECT hl.library_id,
						hl.machine_name,
						hl.major_version,
						hl.minor_version,
						hl.patch_version,
						hl.preloaded_css,
						hl.preloaded_js,
						hnl.drop_css,
						hnl.dependency_type
				FROM h5p_contents_libraries hnl
				JOIN h5p_libraries hl ON hnl.library_id = hl.library_id
				WHERE hnl.content_id = %s
				ORDER BY hnl.weight
			""" % pid)

        result = self.dictfetchall(cursor)
        dependencies = collections.OrderedDict()
        for dependency in result:
            dependencies[dependency['library_id']] = dependency

        return dependencies

    def updateTutorial(self):
        response = json.loads(self.fetchExternalData(
            'https://h5p.org/libraries-metadata.json'))
        libraries = h5p_libraries.objects.values()
        for name, url in response['libraries'].items():
            for library in libraries:
                if library['machine_name'] == name:
                    self.setLibraryTutorialUrl(
                        library['machine_name'], url['tutorialUrl'])

        return 0

    ##
    # Get stored setting
    ##
    def getOption(self, name, default=None):
        return getattr(settings, name, default)

    ##
    # Stores the given setting
    ##
    def setOption(self, name, value):
        setattr(settings, name, value)

    ##
    # Convert variables to fit our DB
    ##
    def camelToString(self, inputValue):
        matches = re.search('[a-z0-9]([A-Z])[a-z0-9]', inputValue)
        if matches:
            matches = re.sub('[a-z0-9]([A-Z])[a-z0-9]', matches.group(1), inputValue)
            return result.lower()
        else:
            return inputValue

    ##
    # This will update selected fields on the given content
    ##
    def updateContentFields(self, pid, fields):
        cursor = connection.cursor()
        for name, value in fields.items():
            query = {
                '{0}'.format(name): value
            }
            h5p_contents.objects.filter(content_id=pid).update(**query)

    ##
    # Not implemented yet
    ##
    def afterExportCreated(self):
        return 0

    ##
    # Will clear filtered params for all the content that uses the specified
    # library. This means that the content dependencies will have to be rebuilt,
    # and the parameters refiltered
    ##
    def clearFilteredParameters(self, libraryId):
        # TODO
        return ''

    ##
    # Get number of contents that has to get their content dependencies rebuilt
    ##
    def getNumNotFiltered(self):
        return int(h5p_contents.objects.filter(filtered='', main_library_id__level__gt=0).values('content_id').count())

    ##
    # Get number of contents using library as main library
    ##
    def getNumContent(self, libraryId):
        return int(h5p_contents.objects.filter(main_library_id=libraryId).values('content_id').count())

    ##
    # Get number of contents
    ##
    def getNumContentPlus(self):
        return int(h5p_contents.objects.values('content_id').count())

    ##
    # Determines if content slug is used
    ##
    def isContentSlugAvailable(self, slug):
        result = h5p_contents.objects.filter(slug=slug).values('slug')
        return False if len(result) > 0 else True

    ##
    # Returns all rows from a cursor as a dict
    ##
    def dictfetchall(self, cursor):
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
