""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
import os
import django
import requests
import zipfile

class H5PDjango:
    def getPlatformInfo(self):
        return {
            "name": "django",
            "version": django.get_version(),
            "h5pVersion": '7.x'
        }

    def fetchExternalData(self, url, data = None, blocking = True, stream = None, allData = False, headers = {}, files = [], method = 'POST'):
        if method == 'POST':
            response = request.post(url, data, headers=headers, files=files)
        else:
            response = request.get(url)

        return respose.content if response.status_code == 200 else response.raise_for_status()

    def setLibraryTutorialUrl(self, machineName, tutorialUrl):
        tutorial = None
        tutorial.tutorial_url = tutorialUrl
        tutorial.save()

    def setErrorMessage(self, message, code = None):
        pass

    def setInfoMessage(self, message):
        pass

    def getMessages(self, type):
        pass

    def t(self, message, replacements = []):
        pass

    def getLibraryFileUrl(self, libraryFolderName, fileName):
        pass

    def getUploadedH5pFolderPath(self):
        pass

    def getUploadedH5pPath(self):
        pass

    def loadAddons(self):
        pass

    def getLibraryConfig(self, libraries = None):
        pass

    def loadLibraries(self):
        pass

    def getAdminUrl(self):
        pass

    def getLibraryId(self, machineName, majorVersion = None, minorVersion = None):
        pass

    def getWhiteList(self, isLibrary, defaultContentWhitelist, defaultLibraryWhitelist):
        pass

    def isPatchedLibrary(self, library):
        pass

    def isInDevMode(self):
        return False

    def mayUpdateLibraries(self):
        pass

    def saveLibraryData(self, libraryData, new = True):
        pass

    def insertContent(self, content, contentMainId = None):
        pass

    def updateContent(self, content, contentMainId = None):
        pass

    def resetContentUserData(self, contentId):
        pass

    def saveLibraryDependencies(self, libraryId, dependencies, dependency_type):
        pass

    def copyLibraryUsage(self, contentId, copyFromId, contentMainId = None):
        pass

    def deleteContentData(self, contentId):
        pass

    def deleteLibraryUsage(self, contentId):
        pass

    def saveLibraryUsage(self, contentId, librariesInUse):
        pass
    
    def getLibraryUsage(self, libraryId, skipContent = False):
        pass

    def loadLibrary(self, machineName, majorVersion, minorVersion):
        pass

    def loadLibrarySemantics(self, machineName, majorVersion, minorVersion):
        pass

    def alterLibrarySemantics(self, semantics, machineName, majorVersion, minorVersion):
        pass

    def deleteLibraryDependencies(self, libraryId):
        pass

    def lockDependencyStorage(self):
        pass

    def unlockDependencyStorage(self):
        pass

    def deleteLibrary(self, library):
        pass

    def loadContent(self, id):
        pass

    def loadContentDependencies(self, id, type = None):
        pass

    def getOption(self, name, default = None):
        pass

    def setOption(self, name, value):
        pass

    def updateContentFields(self, id, fields):
        pass

    def clearFilteredParameters(self, library_ids):
        pass

    def getNumNotFiltered(self):
        pass

    def getNumContent(self, libraryId, skip = None):
        pass

    def isContentSlugAvailable(self, slug):
        pass

    def getLibraryStats(self, type):
        pass
    
    def getNumAuthors(self):
        pass

    def saveCachedAssets(self, library_id):
        pass

    def deleteCachedAssets(self, library_id):
        pass

    def getLibraryContentCount(self):
        pass

    def afterExportCreated(self, content, filename):
        pass

    def hasPermission(self, permission, id = None):
        pass

    def replaceContentTypeCache(self, contentTypeCache):
        pass

    def libraryHasUpgrade(self, library):
        pass

    def replaceContentHubMetadataCache(self, metadata, lang):
        pass

    def getContentHubMetadataChecked(self, lang = 'en'):
        pass
    
    def setContentHubMetadataChecked(self, time, lang = 'en'):
        pass

class H5PValidator:
    h5pRequired = {
        "title": "^.{1, 255}$",
        "language": "^[a-z]{1, 5}$",
        "preloadDependencies": {
            "machineName": "^[\w0-9\-\.]{1, 255}$",
            "majorVersion": "^[0-9]{1, 5}$",
            "minorVersion": "^[0-9]{1, 5}$"
        },
        "mainLibrary": "(?i)^[$a-z_][0-9a-z_\.$]{1, 254}$",
        "embedTypes": {"iframe", "div"}
    }

    h5pOptional = {
        "contentType": "^.{1, 255}$",
        "dynamicDependencies": {
            "machineName": "^[\w0-9\-\.]{1, 255}$",
            "majorVersion": "^[0-9]{1, 5}$",
            "minorVersion": "^[0-9]{1, 5}$"
        },
        "author": "^.{1, 255}$",
        "authors": {
            "name": "^.{1, 255}$",
            "role": "^\w+$"
        },
        "source": "^(http[s]?:\/\/.+)$",
        "license": "^(cc-by|cc-by-sa|cc-by-nd|cc-by-nc|cc-by-nc-sa|cc-by-nc-nd|pd|cr|MIT|GPL1|GPL2|GPL3|MPL|MPL2)$",
        "licenseVersion": "^(1\.0|2\.0|2\.5|3\.0|4\.0)$",
        "licenseExtras": "^.{1,5000}$",
        "yearsFrom": "^([0-9]{1,4})$",
        "yearsTo": "^([0-9]{1,4})$",
        "changes": {
            "date": "^[0-9]{2}-[0-9]{2}-[0-9]{2} [0-9]{1,2}:[0-9]{2}:[0-9]{2}$",
            "author": "^.{1,255}$",
            "log": "^.{1,5000}$"
        },
        "authorComments": "^.{1,5000}$",
        "w": "^[0-9]{1,4}$",
        "h": "^[0-9]{1,4}$",
        "metaKeywords": "^.{1,}$",
        "metaDescription": "^.{1,}$"
    }

    libraryRequired = {
        "title": "^.{1,255}$",
        "majorVersion": "^[0-9]{1,5}$",
        "minorVersion": "^[0-9]{1,5}$",
        "patchVersion": "^[0-9]{1,5}$",
        "machineName": "^[\w0-9\-\.]{1,255}$",
        "runnable": "^(0|1)$"
    }

    libraryOptional = {
        "author": "^.{1,255}$",
        "license": "^(cc-by|cc-by-sa|cc-by-nd|cc-by-nc|cc-by-nc-sa|cc-by-nc-nd|pd|cr|MIT|GPL1|GPL2|GPL3|MPL|MPL2)$",
        "description": "^.{1,}$",
        "metadataSettings": {
            "disable": "^(0|1)$",
            "disableExtraTitleField": "^(0|1)$"
        },
        "dynamicDependencies": {
            "machineName": "^[\w0-9\-\.]{1,255}$i",
            "majorVersion": "^[0-9]{1,5}$",
            "minorVersion": "^[0-9]{1,5}$",
        },
        "preloadedDependencies": {
            "machineName": "^[\w0-9\-\.]{1,255}$i",
            "majorVersion": "^[0-9]{1,5}$",
            "minorVersion": "^[0-9]{1,5}$",
        },
        "editorDependencies": {
            "machineName": "^[\w0-9\-\.]{1,255}$",
            "majorVersion": "^[0-9]{1,5}$",
            "minorVersion": "^[0-9]{1,5}$",
        },
        "preloadedJs": {
            "path": "(?i)^((\\\|\/)?[a-z_\-\s0-9\.]+)+\.js$",
        },
        "preloadedCss": {
            "path": "(?i)^((\\\|\/)?[a-z_\-\s0-9\.]+)+\.css$",
        },
        "dropLibraryCss": {
            "machineName": "^[\w0-9\-\.]{1,255}$",
        },
        "w": "^[0-9]{1,4}$",
        "h": "^[0-9]{1,4}$",
        "embedTypes": {"iframe", "div"},
        "fullscreen": "^(0|1)$",
        "coreApi": {
            "majorVersion": "^[0-9]{1,5}$",
            "minorVersion": "^[0-9]{1,5}$",
        }
    }

    def __init__(self, H5PFramework, H5PCore):
        self.h5pF = H5PFramework
        self.h5pC = H5PCore
        self.h5pCV = H5PContentValidator(self.h5pF, self.h5pC)

    def isValidPackage(self, skipContent = False, upgradeOnly = False):
        tmpDir = self.h5pF.getUploadedH5pFolderPath()
        tmpPath = self.h5pF.getUploadedH5pPath()

        if tmpPath[-3:].lower() != "h5p":
            print("The file you uploaded is not a valid HTML5 package (It does not have the .h5p file extension)")

            self.h5pC.deleteFileTree(tmpDir)

            return False

        zipf = zipfile.ZipFile(tmpPath, "r")

        if zipf:
            zipf.extractAll(tmpDir)
            zipf.close()
        else:
            print("The file you uploaded is not a valid HTML5 package (Unable to unzip it)")

            self.h5pC.deleteFileTree(tmpDir)

            return False

        os.remove(tmpPath)

        valid = True
        libraries = dict()
        files = os.listdir(tmpDir)
        mainH5pData = None
        libraryJsonData = None
        mainH5pExists = imageExists = contentExists = False

        for f in files:
            if f[0:1] in [".", "_"]:
                continue

            filePath = os.path.join(tmpDir, f)

            if f.lower() == "h5p.json":
                if skipContent:
                    continue

                mainH5pData = self.getJsonData(filePath)

                if mainH5pData == False:
                    valid = False

                    print("Could not parse the main h5p.json file")
                else:
                    validH5p = self.isValidH5pData(mainH5pData, f, self.h5pRequired, self.h5pOptional)

                    if validH5p:
                        mainH5pExists = True
                    else:
                        valid = False

                        print("The main h5p.json file is not valid")
            elif f.lower() == "h5p.jpg":
                imageExists = True
            elif f.lower() == "content":
                if skipContent:
                    continue

                if not os.path.isdir(filePath):
                    print("Invalid content folder")

                    valid = False

                    continue

                contentJsonData = self.getJsonData(os.path.join(filePath, "content.json"))

                if contentJsonData == False:
                    print("Could not find or parse the content.json file")

                    valid = False

                    continue
                else:
                    contentExists = True

                if not self.h5pCV.validateContentFiles(filePath):
                    valid = False

                    continue
            elif self.h5pF.mayUpdateLibraries():
                if not os.path.isdir(filePath):
                    continue

                libraryH5PData = self.getLibraryData(f, filePath, tmpDir)

                if libraryH5PData != False:
                    if libraryH5PData["machineName"] != f and self.h5pC.libraryToString(libraryH5PData, True) != f:
                        print("Library directory name must match machineName or machineName-majorVersion.minorVersion (from library.json). (Directory: %s %s %s %s)"%(f, libraryH5PData["machineName"], libraryH5PData["majorVersion"], libraryH5PData["minorVersion"]))

                        valid = False

                        continue

                    libraryH5PData["uploadDirectory"] = filePath
                    libraries[self.h5pC.libraryToString(libraryH5PData)] = libraryH5PData
                else:
                    valid = False

        if not skipContent:
            if not contentExists:
                print("A valid content folder is missing")

                valid = False
            
            if not mainH5pData:
                print("A valid main h5p.json file is missing")

                valid = False

        if valid:
            if upgradeOnly:
                for libString, library in libraries:
                    if self.h5pF.getLibraryId(library["machineName"]) != False:
                        upgrades[libString] = library
                
                missingLibraries = self.getMissingLibraries(upgrades)

                while missingLibraries == True:
                    for libString, missing in missingLibraries:
                        library = libraries[libString]

                        if library:
                            upgrades[libString] = library

                libraries = upgrades

            if not skipContent:
                self.h5pC.mainJsonData = mainH5pData
                self.h5pC.contentJsonData = contentJsonData

                libraries["mainH5pData"] = mainH5pData

            missingLibraries = self.getMissingLibraries(libraries)

            for libString, missing in missingLibraries[0].iteritems():
                if self.h5pC.getLibraryId(missing, libString):
                    del missingLibraries[libString]

            if not empty(missingLibraries[0]):
                for libString, library in missingLibraries[0].iteritems():
                    print("Missing required library %s"%(libString))

                if not self.h5pF.mayUpdateLibraries():
                    print("Note that the libraries may exist in the file you uploaded, but you're not allowed to upload new libraries. Contact the site administrator")

            valid = empty(missingLibraries[0]) and valid

        if not valid:
            self.h5pC.deleteFileTree(tmpDir)

        return valid
