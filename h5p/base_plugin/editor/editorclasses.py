""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
##
# Handles all communication with the database
##
import os
import re
import json
import shutil
import collections
from django.conf import settings

from h5p.models import h5p_libraries

class H5PDjangoEditor:
    global buildBase
    buildBase = None

    ##
    # Constructor for the core editor library
    ##
    def __init__(self, h5p, storage, basePath, filesDir, editorFilesDir=None):
        self.h5p = h5p
        self.storage = storage
        self.basePath = basePath
        self.contentFilesDir = os.path.join(filesDir, 'content')
        self.editorFilesDir = os.path.join(filesDir if editorFilesDir == None else editorFilesDir, 'editor')

    ##
    # This does alot of the same as getLibraries in library/h5pclasses.py. Use that instead ?
    ##
    def getLibraries(self, request):
        if 'libraries[]' in request.POST:
            lib = dict(request.POST.iterlists())
            liblist = list()
            for name in lib['libraries[]']:
                liblist.append(name)
            libraries = list()
            for libraryName in liblist:
                matches = re.search('(.+)\s(\d+)\.(\d+)$', libraryName)
                if matches:
                    libraries.append({
                        'uberName': libraryName,
                        'name': matches.group(1),
                        'majorVersion': matches.group(2),
                        'minorVersion': matches.group(3)
                    })

        libraries = self.storage.getLibraries(
            libraries if 'libraries' in locals() else None)

        if self.h5p.development_mode:
            devLibs = self.h5p.h5pD.getLibraries()

            for i in range(0, len(libraries)):
                if devLibs:
                    lid = libraries[i][
                        'name'] + ' ' + libraries[i]['majorVersion'] + '.' + libraries[i]['minorVersion']
                    if 'lid' in devLibs:
                        libraries[i] = {
                            'uberName': lid,
                            'name': devLibs[lid]['machineName'],
                            'title': devLibs[lid]['title'],
                            'majorVersion': devLibs[lid]['majorVersion'],
                            'minorVersion': devLibs[lid]['minorVersion'],
                            'runnable': devLibs[lid]['runnable'],
                            'restricted': libraries[i]['restricted'],
                            'tutorialUrl': libraries[i]['tutorialUrl'],
                            'isOld': libraries[i]['isOld']
                        }

        return json.dumps(libraries)

    ##
    # Get all scripts, css and semantics data for a library
    ##
    def getLibraryData(self, machineName, majorVersion, minorVersion, langageCode, prefix=''):
        libraries = self.findEditorLibraries(
            machineName, majorVersion, minorVersion)
        libraryData = dict()
        libraryData['semantics'] = self.h5p.loadLibrarySemantics(
            machineName, majorVersion, minorVersion)
        libraryData['language'] = self.getLibraryLanguage(
            machineName, majorVersion, minorVersion, langageCode)

        aggregateAssets = self.h5p.aggregateAssets
        self.h5p.aggregateAssets = False

        files = self.h5p.getDependenciesFiles(libraries)

        self.h5p.aggregateAssets = aggregateAssets

        # Create base URL
        url = settings.BASE_URL + '/media/h5pp' + prefix

        # JavaScripts
        if 'scripts' in files:
            for script in files['scripts']:
                if re.search('/:\/\//', script['path']):
                    # External file
                    if not 'javascript' in libraryData:
                        libraryData['javascript'] = collections.OrderedDict()
                    libraryData['javascript'][script['path'] + script['version']] = '\n' + script['path'].read()
                else:
                    # Local file
                    if not 'javascript' in libraryData:
                        libraryData['javascript'] = collections.OrderedDict()
                    libraryData['javascript'][
                        url + script['path'] + script['version']] = '\n' + self.h5p.fs.getContent(script['path'])

        # Stylesheets
        if 'styles' in files:
            for css in files['styles']:
                if re.search('/:\/\//', css['path']):
                    # External file
                    if not 'css' in libraryData:
                        libraryData['css'] = dict()
                    libraryData['css'][css['path'] + css['version']] = css['path'].read()
                else:
                    # Local file
                    if not 'css' in libraryData:
                        libraryData['css'] = dict()
                    self.buildCssPath(
                        None, url + os.path.dirname(css['path']) + '/')
                    libraryData['css'][url + css['path'] + css['version']] = re.sub(
                        '(?i)url\([\']?(?![a-z]+:|\/+)([^\')]+)[\']?\)', self.buildCssPath, self.h5p.fs.getContent(css['path']))

        # Add translations for libraries
        for key, library in libraries.iteritems():
            language = self.getLibraryLanguage(library['machine_name'], library[
                                            'major_version'], library['minor_version'], langageCode)
            if language != None:
                lang = '; H5PEditor.language["' + \
                    library['machine_name'] + '"] = ' + language + ';'
                libraryData['javascript'][lang] = lang

        return json.dumps(libraryData)

    ##
    # Return all libraries used by the given editor library
    ##
    def findEditorLibraries(self, machineName, majorVersion, minorVersion):
        library = self.h5p.loadLibrary(machineName, majorVersion, minorVersion)
        dependencies = dict()
        self.h5p.findLibraryDependencies(dependencies, library)

        # Order dependencies by weight
        orderedDependencies = collections.OrderedDict()
        for i in range(1, len(dependencies) + 1):
            for key, dependency in dependencies.iteritems():
                if dependency['weight'] == i and dependency['type'] == 'editor':
                    # Only load editor libraries
                    dependency['library']['id'] = dependency[
                        'library']['library_id']
                    orderedDependencies[dependency['library'][
                        'library_id']] = dependency['library']
                    break

        return orderedDependencies

    def getLibraryLanguage(self, machineName, majorVersion, minorVersion, langageCode):
        language = self.storage.getLanguage(
            machineName, majorVersion, minorVersion, langageCode)
        return None if language == False else language

    ##
    # Create directories for uploaded content
    ##
    def createDirectories(self, contentId):
        self.contentDirectory = os.path.join(
            self.contentFilesDir, str(contentId))
        if not os.path.isdir(self.contentFilesDir):
            os.mkdir(os.path.join(self.basePath, self.contentFilesDir), 0o777)

        subDirectories = ['', 'files', 'images', 'videos', 'audios']
        for subDirectory in subDirectories:
            subDirectory = os.path.join(self.contentDirectory, subDirectory)
            if not os.path.isdir(subDirectory):
                os.mkdir(subDirectory)

        return True

    ##
    # Move uploaded files, remove old files and update library usage
    ##
    def processParameters(self, contentId, newLibrary, newParameters, oldLibrary=None, oldParameters=None):
        newFiles = list()
        oldFiles = list()
        field = {
            'type': 'library'
        }
        libraryParams = {
            'library': self.h5p.libraryToString(newLibrary),
            'params': newParameters
        }
        self.processField(field, libraryParams, newFiles)
        if oldLibrary != None:
            self.processSemantics(oldFiles, self.h5p.loadLibrarySemantics(oldLibrary[
                                'name'], oldLibrary['majorVersion'], oldLibrary['minorVersion'], oldParameters))

            for i in range(0, len(oldFiles)):
                if not oldFiles[i] in newFiles and not re.search('(?i)^(\w+:\/\/|\.\.\/)', oldFiles[i]):
                    removeFile = self.contentDirectory + oldFiles[i]
                    del(removeFile)
                    self.storage.removeFile(removeFile)

    ##
    # Recursive function that moves the new files in to the h5p content folder and generates a list over the old files
    # Also locates all the libraries
    ##
    def processSemantics(self, files, semantics, params):
        for i in range(0, len(semantics)):
            field = semantics[i]
            if not field['name'] in params:
                continue
            self.processField(field, params[field['name']], files)

    ##
    # Process a single field
    ##
    def processField(self, field, params, files):
        if field['type'] == 'image' or field['type'] == 'file':
            if 'path' in params:
                self.processFile(params, files)
                if 'originalImage' in params and 'path' in params['originalImage']:
                    self.processFile(params['originalImage'], files)
            return
        elif field['type'] == 'audio' or field['type'] == 'video':
            if isinstance(params, list):
                for i in range(0, len(params)):
                    self.processFile(params[i], files)
            return
        elif field['type'] == 'library':
            if 'library' in params and 'params' in params:
                library = self.libraryFromString(params['library'])
                semantics = self.h5p.loadLibrarySemantics(library['machineName'], library['majorVersion'], library['minorVersion'])
                self.processSemantics(files, semantics, params['params'])
            return
        elif field['type'] == 'group':
            if params:
                if len(field['fields']) == 1:
                    params = {
                        field['fields'][0]['name']: params
                    }
                self.processSemantics(files, field['fields'], params)
            return
        elif field['type'] == 'list':
            if isinstance(params, list):
                for j in range(0, len(params)):
                    self.processField(field['field'], params[j], files)
            return
        return

    def processFile(self, params, files):
        editorPath = self.editorFilesDir

        matches = re.search(self.h5p.relativePathRegExp, params['path'])
        if matches:
            source = os.path.join(self.contentDirectory, matches.group(
                1), matches.group(4), matches.group(5))
            dest = os.path.join(self.contentDirectory, matches.group(5))
            if os.path.exists(source) and not os.path.exists(dest):
                shutil.copy(source, dest)

            params['path'] = matches.group(5)
        else:
            oldPath = os.path.join(self.basePath, editorPath, params['path'])
            newPath = os.path.join(
                self.basePath, self.contentDirectory, params['path'])
            if not os.path.exists(newPath) and os.path.exists(oldPath):
                shutil.copy(oldPath, newPath)

        files.append(params['path'])

    ##
    # This function will prefix all paths within a css file.
    ##
    def buildCssPath(self, matches, base=None):
        global buildBase
        if base != None:
            buildBase = base

        if matches == None:
            return

        dirr = re.sub('(css/|styles/|Styles/|Css/)', 'fonts/', buildBase)
        path = dirr + matches.group(1)

        return 'url(' + path + ')'

    ##
    # Parses library data from a string on the form {machineName} {majorVersion}.{minorVersion}
    ##
    def libraryFromString(self, libraryString):
        pre = '^([\w0-9\-\.]{1,255})[\-\ ]([0-9]{1,5})\.([0-9]{1,5})$'
        res = re.search(pre, libraryString)
        if res:
            return {
                'machineName': res.group(1),
                'majorVersion': res.group(2),
                'minorVersion': res.group(3)
            }
        return False
