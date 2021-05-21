import os
import re
import cgi
import html
import json
import glob
import math
import time
import uuid
import pprint
import binascii
import hashlib
import zipfile
import urllib.request
from django.template.defaultfilters import slugify

from .development import H5PDevelopment
from .defaultstorage import H5PDefaultStorage

is_array = lambda var: isinstance(var, (list, tuple))

def empty(variable):
    if not variable:
        return True
    return False

def substr_replace(subject, replace, start, length):
    if length == None:
        return subject[:start] + replace
    elif length < 0:
        return subject[:start] + replace + subject[length:]
    else:
        return subject[:start] + replace + subject[start + length:]

def file_get_contents(filename, use_include_path=0, context=None, offset=-1, maxlen=-1):
    if (filename.find("://") > 0):
        ret = urllib.request.urlopen(filename).read()
        if (offset > 0):
            ret = ret[offset:]
        if (maxlen > 0):
            ret = ret[:maxlen]
        return ret
    else:
        fp = open(filename, "rb")
        try:
            if (offset > 0):
                fp.seek(offset)
            ret = fp.read(maxlen)
            return ret
        finally:
            fp.close()

##
# self class is used for validating H5P files
##
class H5PValidator:
    h5pRequired = {
        "title": "^.{1,255}$",
        "language": "^[a-z]{1,5}$",
        "preloadedDependencies": {
            "machineName": "^[\w0-9\-\.]{1,255}$",
            "majorVersion": "^[0-9]{1,5}$",
            "minorVersion": "^[0-9]{1,5}$"
        },
        "mainLibrary": "(?i)^[$a-z_][0-9a-z_\.$]{1,254}$",
        "embedTypes": {"iframe", "div"}
    }

    h5pOptional = {
        "contentType": "^.{1,255}$",
        "author": "^.{1,255}$",
        "license": "^(cc-by|cc-by-sa|cc-by-nd|cc-by-nc|cc-by-nc-sa|cc-by-nc-nd|pd|cr|MIT|GPL1|GPL2|GPL3|MPL|MPL2|U)$",
        "dynamicDependencies": {
            "machineName": "^[\w0-9\-\.]{1,255}$",
            "majorVersion": "^[0-9]{1,5}$",
            "minorVersion": "^[0-9]{1,5}$"
        },
        "w": "^[0-9]{1,4}$",
        "n": "^[0-9]{1,4}$",
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
        "license": "^(cc-by|cc-by-sa|cc-by-nd|cc-by-nc|cc-by-nc-sa|cc-by-nc-nd|pd|cr|MIT|GPL1|GPL2|GPL3|MPL|MPL2|U)$",
        "description": "^.{1,}$",
        "dynamicDependencies": {
            "machineName": "^[\w0-9\-\.]{1,255}$",
            "majorVersion": "^[0-9]{1,5}$",
            "minorVersion": "^[0-9]{1,5}$"
        },
        "preloadedDependencies": {
            "machineName": "^[\w0-9\-\.]{1,255}$",
            "majorVersion": "^[0-9]{1,5}$",
            "minorVersion": "^[0-9]{1,5}$"
        },
        "editorDependencies": {
            "machineName": "^[\w0-9\-\.]{1,255}$",
            "majorVersion": "^[0-9]{1,5}$",
            "minorVersion": "^[0-9]{1,5}$"
        },
        "preloadedJs": {
            "path": "(?i)^((\/)?[a-z_\-\s0-9\.]+)+\.js$"
        },
        "preloadedCss": {
            "path": "(?i)^((\/)?[a-z_\-\s0-9\.]+)+\.css$"
        },
        "dropLibraryCss": {
            "machineName": "^[\w0-9\-\.]{1,255}$"
        },
        "w": "^[0-9]{1,4}$",
        "h": "^[0-9]{1,4}$",
        "embedTypes": {"iframe", "div"},
        "fullscreen": "^(0|1)$",
        "coreApi": {
            "majorVersion": "^[0-9]{1,5}$",
            "minorVersion": "^[0-9]{1,5}$"
        }
    }

    ##
    # Constructor for the H5PValidator
    ##
    def __init__(self, H5PFramework, H5PCore):
        self.h5pF = H5PFramework
        self.h5pC = H5PCore
        self.h5pCV = H5PContentValidator(self.h5pF, self.h5pC)

    ##
    # Validates a .h5p file
    ##
    def isValidPackage(self, skipContent=False, upgradeOnly=False):

        # Create a temporary dir to extract package in.
        tmpDir = self.h5pF.getUploadedH5pFolderPath()
        tmpPath = self.h5pF.getUploadedH5pPath()

        # Only allow files with the .h5p extension.
        if tmpPath[-3:].lower() != "h5p":
            print(
                "The file you uploaded is not a valid HTML5 Package (It does not have the .h5p file extension)")
            self.h5pC.deleteFileTree(tmpDir)
            return False

        zipf = zipfile.ZipFile(tmpPath, "r")
        if zipf:
            zipf.extractall(tmpDir)
            zipf.close()
        else:
            print(
                "The file you uploaded is not a valid HTML5 Package (We are unable to unzip it)")
            self.h5pC.deleteFileTree(tmpDir)
            return False

        os.remove(tmpPath)

        # Process content and libraries
        valid = True
        libraries = dict()
        files = os.listdir(tmpDir)
        mainH5pData = None
        libraryJsonData = None
        contentJsonData = None
        mainH5pExists = imageExists = contentExists = False
        for f in files:
            if f[0:1] in [".", "_"]:
                continue

            filePath = tmpDir + "/" + f
            # Check for h5p.json file.
            if f.lower() == "h5p.json":
                if skipContent == True:
                    continue

                mainH5pData = self.getJsonData(filePath)
                if mainH5pData == False:
                    valid = False
                    print(
                        "Could not parse the main h5p.json file")
                else:
                    validH5p = self.isValidH5pData(
                        mainH5pData, f, self.h5pRequired, self.h5pOptional)
                    if validH5p:
                        mainH5pExists = True
                    else:
                        valid = False
                        print(
                            "The main h5p.json file is not valid")

            # Check for h5p.jpg ?
            elif f.lower() == "h5p.jpg":
                imageExists = True

            # Content directory holds content.
            elif f == "content":
                # We do a separate skipContent check to avoid having the
                # content folder being treated as a library.
                if skipContent:
                    continue
                if not os.path.isdir(filePath):
                    print(
                        "Invalid content folder")
                    valid = False
                    continue

                contentJsonData = self.getJsonData(
                    filePath + "/" + "content.json")

                if contentJsonData == False:
                    print(
                        "Could not find or parse the content.json file")
                    valid = False
                    continue
                else:
                    contentExists = True
                    # In the future we might left the libraries provide
                    # validation functions for content.json.

                if not self.h5pCV.validateContentFiles(filePath):
                    # validateContentFiles adds potential errors to the queue
                    valid = False
                    continue

            # The rest should be library folders.
            elif self.h5pF.mayUpdateLibraries():
                if not os.path.isdir(filePath):
                    # Ignore self. Probably a file that shouldn"t have been
                    # included.
                    continue

                libraryH5PData = self.getLibraryData(f, filePath, tmpDir)
                
                if libraryH5PData != False:
                    # Library"s directory name must be:
                    # - <machineName>
                    #      - or -
                    # - <machineName>-<majorVersion>.<minorVersion>
                    # where machineName, majorVersion and minorVersion is read
                    # from library.json
                    if libraryH5PData["machineName"] != f and self.h5pC.libraryToString(libraryH5PData, True) != f:
                        print("""Library directory name must match machineName or machineName-majorVersion.minorVersion (from library.json). (Directory:
                %s
                %s
                %s
                %s)""" % (f, libraryH5PData["machineName"], libraryH5PData["majorVersion"], libraryH5PData["minorVersion"]))
                        valid = False
                        continue
                    
                    libraryH5PData["uploadDirectory"] = filePath
                    libraries[self.h5pC.libraryToString(libraryH5PData)] = libraryH5PData
                else:
                    valid = False

        if skipContent == False:
            if not contentExists:
                print(
                    "A valid content folder is missing")
                valid = False
            if not mainH5pExists:
                print(
                    "A valid main h5p.json file is missing")
                valid = False

        if valid:
            if upgradeOnly:
                # When upgrading, we only add the already installed libraries, and
                # the new dependent libraries
                for libString, library in libraries:
                    # Is self library already installed ?
                    if self.h5pF.getLibraryId(library["machineName"]) != False:
                        upgrades[libString] = library

                missingLibraries = self.getMissingLibraries(upgrades)
                while missingLibraries == True:
                    for libString, missing in missingLibraries:
                        library = libraries[libString]
                        if library:
                            upgrades[libString] = library

                libraries = upgrades

            self.h5pC.librariesJsonData = dict(libraries)

            if skipContent == False:
                self.h5pC.mainJsonData = mainH5pData
                self.h5pC.contentJsonData = contentJsonData
                # Check for the dependencies in h5p.json as well as in the
                # libraries
                libraries["mainH5pData"] = mainH5pData

            missingLibraries = self.getMissingLibraries(libraries)

            for libString, missing in missingLibraries[0].items():
                if self.h5pC.getLibraryId(missing, libString):
                    del missingLibraries[libString]

            if not empty(missingLibraries[0]):
                for libString, library in missingLibraries[0].items():
                    print(
                        "Missing required library %s" % (libString))
                if not self.h5pF.mayUpdateLibraries():
                    print(
                        "Note that the libraries may exist in the file you uploaded, but you\"re not allowed to upload new libraries. Contact the site administrator about self.")

            valid = empty(missingLibraries[0]) and valid

        if not valid:
            self.h5pC.deleteFileTree(tmpDir)
        return valid

    ##
    # Validates a H5P library
    ##
    def getLibraryData(self, f, filePath, tmpDir):
        if not re.search("^[\w0-9\-\.]{1,255}$", f):
            print(
                "Invalid library name: %s" % (f))
            return False

        h5pData = self.getJsonData(filePath + "/" + "library.json")

        if h5pData == False:
            print(
                "Could not find library.json file with valid json format for library %s" % (f))
            return False

        # validate json if a semantics file is provided
        semanticsPath = filePath + "/" + "semantics.json"

        if os.path.exists(semanticsPath):
            semantics = self.getJsonData(semanticsPath, True)
            if semantics == False:
                print(
                    "Invalid semantics.json file has been included in the library %s" % (f))
                return False
            else:
                h5pData["semantics"] = semantics

        # validate language folder if it exists
        languagePath = filePath + "/" + "language"

        if os.path.exists(languagePath):
            languageFiles = os.listdir(languagePath)
            for languageFile in languageFiles:
                if languageFile in [".", ".."]:
                    continue
                if not re.search("^(-?[a-z]+){1,7}\.json$", languageFile):
                    print(
                        "Invalid language file %s in library %s" % (languageFile, f))
                    return False

                languageJson = self.getJsonData(
                    languagePath + "/" + languageFile, True)

                if languageJson == False:
                    print(
                        "Invalid language file %s has been included in the library %s" % (languageFile, f))
                    return False

                # parts[0] is the language code
                parts = languageFile.split(".")
                lang = {parts[0]: languageJson}
                if not "language" in h5pData:
                    h5pData[u"language"] = lang
                else:
                    h5pData["language"][parts[0]] = languageJson

        validLibrary = self.isValidH5pData(
            h5pData, f, self.libraryRequired, self.libraryOptional)

        validLibrary = self.h5pCV.validateContentFiles(filePath, True)

        if "preloadedJs" in h5pData:
            validLibrary = self.isExistingFiles(
                h5pData["preloadedJs"], tmpDir, f) and validLibrary
        if "preloadedCss" in h5pData:
            validLibrary = self.isExistingFiles(
                h5pData["preloadedCss"], tmpDir, f) and validLibrary
        if validLibrary:
            return h5pData
        else:
            return False

    ##
    # Use the dependency declarations to find any missing libraries
    ##
    def getMissingLibraries(self, libraries):
        missing = []
        for library, content in libraries.items():
            if "preloadedDependencies" in content:
                missing.append(self.getMissingDependencies(
                    content["preloadedDependencies"], libraries))
            if "dynamicDependencies" in content:
                missing.append(self.getMissingDependencies(
                    content["dynamicDependencies"], libraries))
            if "editorDependencies" in content:
                missing.append(self.getMissingDependencies(
                    content["editorDependencies"], libraries))
        return missing

    ##
    # Helper function for getMissingLibraries for dependency required libraries in
    # the provided list of libraries
    ##
    def getMissingDependencies(self, dependencies, libraries):
        missing = dict()
        for dependency in dependencies:
            libString = self.h5pC.libraryToString(dependency)
            if not libString in libraries:
                missing[libString] = dependency
        return missing

    ##
    # Figure out if the provided file paths exists
    #
    # Triggers error messages if files doesn"t exist
    ##
    def isExistingFiles(self, files, tmpDir, library):
        for f in files:
            path = f["path"].replace("\\", "/")
            if not os.path.exists(tmpDir + "/" + library + "/" + path):
                print(
                    "The file %s is missing from library: %s" % (path, library))
                return False
        return True

    ##
    # Validates h5p.json and library.json h5p data
    #
    # Error message are triggered if the data isn"t valid
    ##
    def isValidH5pData(self, h5pData, library_name, required, optional):
        valid = self.isValidRequiredH5pData(h5pData, required, library_name)
        valid = self.isValidOptionalH5pData(
            h5pData, optional, library_name) and valid

        # Check the library"s required API version of Core.
        # If no requirement is set self implicitly means 1.0.
        if "coreApi" in h5pData and not empty(h5pData["coreApi"]):
            if h5pData["coreApi"]["majorVersion"] > self.h5pC.coreApi["majorVersion"] or (h5pData["coreApi"]["majorVersion"] == self.h5pC.coreApi["majorVersion"] and
                                                                                        h5pData["coreApi"]["minorVersion"] > self.h5pC.coreApi["minorVersion"]):

                print(
                    "The system was unable to install the %s component from the package, it requires a newer version of the H5P plugin. self site is currently running version %s, whereas the required version is %s or higher. You should consider upgrading and then try again." %
                    (h5pData["title"] if h5pData["title"] else library_name,
                    str(self.h5pC.coreApi["majorVersion"]) + "." +
                    str(self.h5pC.coreApi["minorVersion"]),
                    str(h5pData["coreApi"]["majorVersion"]) +
                    "." + str(h5pData["coreApi"]["minorVersion"])
                    )
                )

                valid = False

        return valid

    ##
    # Helper function for isValidH5pData
    #
    # Validates the optional part of the h5pData
    #
    # Triggers error messages
    ##
    def isValidOptionalH5pData(self, h5pData, requirements, library_name):
        valid = True

        for key, value in h5pData.items():
            if key in requirements:
                valid = self.isValidRequirement(
                    value, requirements[key], library_name, key) and valid
        return valid

    ##
    # Validate a requirement given as regexp or an array of requirements
    ##
    def isValidRequirement(self, h5pData, requirement, library_name, property_name):
        valid = True

        if isinstance(requirement, str):
            if requirement == "boolean":
                if not isinstance(h5pData, bool):
                    print(
                        "Invalid data provided for %s in %s. Boolean expected." % (property_name, library_name))
                    valid = False
            else:
                # The requirement is a regexp, match it against the data
                if isinstance(h5pData, str) or isinstance(h5pData, int):
                    if not re.search(requirement, str(h5pData)):
                        print(
                            "Invalid data provided for %s in %s. No Matches between %s and %s" % (property_name, library_name, requirement, h5pData))
                        valid = False
                else:
                    print(
                        "Invalid data provided for %s in %s. String or Integer expected." % (property_name, library_name))
                    valid = False
        elif isinstance(requirement, dict) or isinstance(requirement, set):
            # we have sub requirements
            if isinstance(h5pData, list):
                if isinstance(h5pData[0], dict):
                    for sub_h5pData in h5pData:
                        valid = self.isValidRequiredH5pData(
                            sub_h5pData, requirement, library_name) and valid
                else:
                    valid = self.isValidRequiredH5pData(
                        h5pData[0], requirement, library_name) and valid

            elif isinstance(h5pData, dict):
                valid = self.isValidRequiredH5pData(
                    h5pData, requirement, library_name) and valid

            else:
                print(
                    "Invalid data provided for %s in %s." % (property_name, library_name))
                valid = False

        else:
            print(
                "Can\"t read the property %s in %s." % (property_name, library_name))
            valid = False

        return valid

    ##
    # Validates the required h5p data in library.json and h5p.json
    ##
    def isValidRequiredH5pData(self, h5pData, requirements, library_name):
        valid = True
        if isinstance(requirements, dict):
            for required, requirement in requirements.items():
                if isinstance(required, int):
                    # We have an array of allowed options
                    return self.isValidH5pDataOptions(h5pData, requirements, library_name)
                if required in h5pData:
                    valid = self.isValidRequirement(
                        h5pData[required], requirement, library_name, required) and valid
                else:
                    print(
                        "The required property %s is missing from %s" % (required, library_name))
                    valid = False
        return valid

    ##
    # Validates h5p data against a set of allowed values(options)
    ##
    def isValidH5pDataOptions(selected, allowed, library_name):
        valid = True
        for value in selected:
            if not value in allowed:
                print(
                    "Illegal option %s in %s." % (value, library_name))
                valid = False
        return valid

    ##
    # Fetch json data from file
    ##
    def getJsonData(self, filePath, return_as_string=False):
        jsonFile = file_get_contents(filePath)
        if jsonFile == False:
            return False  # Cannot read from file.

        jsonData = json.loads(jsonFile)
        if jsonData == None:
            return False

        return jsonFile if return_as_string else jsonData

##
# self class is used for saving H5P files
##
class H5PStorage:
    contentId = None  # Quick fix so WP can get ID of new content.

    ##
    # Constructeur for the H5PStorage
    ##
    def __init__(self, H5PFramework, H5PCore):
        self.h5pF = H5PFramework
        self.h5pC = H5PCore

    ##
    # Saves a H5P file
    ##
    def savePackage(self, content=None, contentMainId=None, skipContent=False, options=dict()):
        if self.h5pF.mayUpdateLibraries():
            # Save the libraries we processed during validation
            self.saveLibraries()
        if not skipContent:
            basePath = self.h5pF.getUploadedH5pFolderPath()
            current_path = basePath + "/content"

            # Save content
            if content == None:
                content = dict()

            if not isinstance(content, dict):
                content = {"id": content}

            # Find main library version
            for dep in self.h5pC.mainJsonData["preloadedDependencies"]:
                if dep["machineName"] == self.h5pC.mainJsonData["mainLibrary"]:
                    dep["libraryId"] = self.h5pC.getLibraryId(dep)
                    content["library"] = dep
                    break

            content["params"] = file_get_contents(
                current_path + "/" + "content.json")

            if "disable" in options:
                content["disable"] = options["disable"]

            if "title" in options:
                content["title"] = options["title"]

            content['author'] = "Amadeus"

            contentId = self.h5pC.saveContent(content, contentMainId)

            self.contentId = contentId

            if not self.h5pC.fs.saveContent(current_path, contentId):
                return False

            # Remove temp content folder
            self.h5pC.deleteFileTree(basePath)

        return True

    ##
    # Helps savePackage.
    ##
    def saveLibraries(self):
        # Keep track of the number of libraries that have been saved
        newOnes = 0
        oldOnes = 0
        # Go through libraries that came with self package
        for libString, library in self.h5pC.librariesJsonData.items():
            # Find local library identifier
            libraryId = self.h5pC.getLibraryId(library, libString)

            # Assume new library
            new = True
            if libraryId != None:
                # Found old library
                library["libraryId"] = libraryId

                if self.h5pF.isPatchedLibrary(library):
                    # self is a newer version than ours. Upgrade !
                    new = False
                else:
                    library["saveDependencies"] = False
                    # self is an older version, no need to save.
                    self.h5pC.deleteFileTree(library['uploadDirectory'])
                    continue

            else:
                print("Ajout de : " + libString)
            # Indicate that the dependencies of self library should be saved.
            library["saveDependencies"] = True
            # Save library meta data
            self.h5pF.saveLibraryData(library, new)
            # Save library folder
            self.h5pC.fs.saveLibrary(library)

            # Remove cached assets that uses self library
            if self.h5pC.aggregateAssets and library["libraryId"]:
                removedKeys = self.h5pF.deleteCachedAssets(
                    library["libraryId"])
                self.h5pC.fs.deleteCachedAssets(removedKeys)

            # Remove tmp folder
            print(library['uploadDirectory'])
            self.h5pC.deleteFileTree(library["uploadDirectory"])

            if new:
                newOnes += 1
            else:
                oldOnes += 1

        # Go through the libraries again to save dependencies.
        for libstring, library in self.h5pC.librariesJsonData.items():
            if not library["saveDependencies"]:
                continue

            # TODO: Should the table be locked for self operation ?

            # Remove any old dependencies
            self.h5pF.deleteLibraryDependencies(library["libraryId"])

            # Insert the different new ones
            if "preloadedDependencies" in library:
                self.h5pF.saveLibraryDependencies(library["libraryId"], library[
                                                "preloadedDependencies"], "preloaded")
            if "dynamicDependencies" in library:
                self.h5pF.saveLibraryDependencies(library["libraryId"], library[
                                                "dynamicDependencies"], "dynamic")
            if "editorDependencies" in library:
                self.h5pF.saveLibraryDependencies(library["libraryId"], library[
                                                "editorDependencies"], "editor")

            # Make sure libraries dependencies, parameter filtering and export
            # files get regenerated for all content who uses self library.
            self.h5pF.clearFilteredParameters(library["libraryId"])

        # Tell the user what we"ve done.
        message = ''
        if newOnes and oldOnes:
            message = "Added %s new H5P libraries and updated %s old." % (
                newOnes, oldOnes)
        elif newOnes:
            message = "Added %s new H5P libraries." % (newOnes)
        elif oldOnes:
            message = "Updated %s H5P libraries." % (oldOnes)

        if message != '':
            print(message)

    ##
    # Delete an H5P package
    ##
    def deletePackage(self, content):
        self.h5pC.fs.deleteContent(content.content_id)
        self.h5pC.fs.deleteExport(
            (content.slug + "-" if content.slug else "") + str(content.content_id) + ".h5p")
        self.h5pF.deleteContentData(content.content_id)

    ##
    # Copy/clone an H5P package
    #
    # May for instance be used if the content is being revisioned without
    # uploading a new H5P package
    ##
    def copyPackage(contentId, copyFromId, contentMainId=None):
        self.h5pC.fs.cloneContent(copyFromId, contentId)
        self.h5pF.copyLibraryUsage(contentId, copyFromId, contentMainId)

##
# self class is used for exporting zips
##


class H5PExport:

    ##
    # Constructor for the H5PExport
    ##
    def __init__(self, H5PFramework, H5PCore):
        self.h5pF = H5PFramework
        self.h5pC = H5PCore

    ##
    # Return path to h5p package.
    #
    # Creates package if not already created
    ##
    def createExportFile(self, content):

        # Get path to temporary folder, where export will be contained
        tmpPath = self.h5pC.fs.getTmpPath()
        os.mkdir(tmpPath, 0o777)

        try:
            # Create content folder and populate with files
            self.h5pC.fs.exportContent(content["id"], tmpPath + "/content")
        except:
            print(
                "Error during the creation of content folder !")
            self.h5pC.deleteFileTree(tmpPath)
            return False

        # Update content.json with content from database
        with open(tmpPath + "/content/content.json", "w") as f:
            f.write(content["params"])

        # Make embedType into an array
        embedTypes = content["embedType"].split(", ")

        # Build h5p.json
        h5pJson = {
            "title": content["title"],
            "language": content["language"] if 'language' in content and len(content["language"].strip()) != 0 else "und",
            "mainLibrary": content["library"]["name"],
            "embedTypes": embedTypes
        }

        # Add dependencies to h5p
        for key, dependency in content["dependencies"].items():
            library = dependency["library"]

            try:
                exportFolder = None

                # Determine path of export library
                if self.h5pC in locals() and self.h5pC.h5pD in locals():
                    # Tries to find library in development folder
                    isDevLibrary = self.h5pC.h5pD.getLibrary(
                        library["machineName"],
                        library["majorVersion"],
                        library["minorVersion"]
                    )

                    if isDevLibrary == None:
                        exportFolder = "/" + library["path"]

                # Export required libraries
                self.h5pC.fs.exportLibrary(library, tmpPath, exportFolder)
            except:
                print(
                    "Error during export the required libraries !")
                self.h5pC.deleteFileTree(tmpPath)
                return False

            # Do not add editor dependencies to h5p json.
            if dependency["type"] == "editor":
                continue

            # Add to h5p.json dependencies
            if not dependency["type"] + "Dependencies" in h5pJson:
                h5pJson[dependency["type"] + "Dependencies"] = list()
            h5pJson[dependency["type"] + "Dependencies"].append({
                "machineName": library["machine_name"],
                "majorVersion": library["major_version"],
                "minorVersion": library["minor_version"]
            })

        # Save h5p.json
        results = json.dumps(h5pJson)
        with open(tmpPath + "/h5p.json", "w") as f:
            f.write(results)

        # Get a complete file list from our tmp dir
        files = list()
        self.populateFileList(tmpPath, files)

        # Get path to temporary export target file
        tmpFile = self.h5pC.fs.getTmpPath()

        # Create new zip instance
        zipf = zipfile.ZipFile(tmpFile, 'w')

        # Add all the files from the tmp dir.
        for f in files:
            # Please not that the zip format has no concept of folders, we must
            # use forward slashes to separate our directories.
            zipf.write(f['absolutePath'], f['relativePath'])

        # Close zip and remove tmp dir
        zipf.close()
        self.h5pC.deleteFileTree(tmpPath)

        try:
            # Save export
            self.h5pC.fs.saveExport(
                tmpFile, content["slug"] + "-" + content["id"] + ".h5p")
        except:
            print(
                "Error during export save !")
            return False

        os.remove(tmpFile)
        self.h5pF.afterExportCreated()

        return True

    ##
    # Recursive function the will add the files of the given directory to the
    # given files list. All files are objects with an absolute path and
    # a relative path. The relative path is forward slashes only ! Great for
    # use in zip files and URLs.
    ##
    def populateFileList(self, directory, files, relative=""):
        strip = len(directory) + 1
        contents = glob.glob(directory + '/' + '*')
        if contents:
            for f in contents:
                rel = relative + f[strip:strip + len(directory)]
                if os.path.isdir(f):
                    self.populateFileList(f, files, rel + '/')
                else:
                    files.append({
                        'absolutePath': f,
                        'relativePath': rel
                    })

    ##
    # Delete .h5p file
    ##
    def deleteExport(content):
        ##
        # Add editor libraries to the list of libraries
        #
        # These are not supposed to go into h5p.json, but must be included with the rest
        # of the libraries
        #
        # TODO self is a function that is not currently being used
        ##
        def addEditorLibraries(libraries, editorLibraries):
            for editorLibrary in editorLibraries:
                libraries[editorLibrary["machineName"]] = editorLibrary
            return libraries

##
# Functions and storage shared by the other H5P classes
##
class H5PCore:
    coreApi = {
        "majorVersion": 1,
        "minorVersion": 19
    }

    styles = [
        "styles/h5p.css",
        "styles/h5p-confirmation-dialog.css",
        "styles/h5p-core-button.css"
    ]

    scripts = [
        "js/jquery.js",
        "js/h5p.js",
        "js/h5p-event-dispatcher.js",
        "js/h5p-x-api-event.js",
        "js/h5p-x-api.js",
        "js/h5p-content-type.js",
        "js/h5p-confirmation-dialog.js"
    ]

    defaultContentWhitelist = "json png jpg jpeg gif bmp tif tiff svg eot ttf woff woff2 otf webm mp4 ogg mp3 wav txt pdf rtf doc docx xls xlsx ppt pptx odt ods odp xml csv diff patch swf md textile"
    defaultLibraryWhitelistExtras = "js css"

    SECONDS_IN_WEEK = 604800

    # Disable flags
    DISABLE_NONE = 0
    DISABLE_FRAME = 1
    DISABLE_DOWNLOAD = 2
    DISABLE_EMBED = 4
    DISABLE_COPYRIGHT = 8
    DISABLE_ABOUT = 16

    DISPLAY_OPTION_FRAME = 'frame'
    DISPLAY_OPTION_DOWNLOAD = 'export'
    DISPLAY_OPTION_EMBED = 'embed'
    DISPLAY_OPTION_COPYRIGHT = 'copyright'
    DISPLAY_OPTION_ABOUT = 'icon'

    global libraryIdMap
    libraryIdMap = dict()

    ##
    # Constructor for the H5PCore
    ##
    def __init__(self, H5PFramework, path, url, language="en", export=False, development_mode=H5PDevelopment.MODE_NONE):
        self.h5pF = H5PFramework

        self.fs = H5PDefaultStorage(path)

        self.url = url
        self.exportEnabled = export
        self.development_mode = development_mode
        self.disableFileCheck = False

        self.aggregateAssets = False  # Off by default.. for now

        if development_mode and H5PDevelopment.MODE_LIBRARY:
            self.h5pD = H5PDevelopment(self.h5pF, path + "/", language)

        self.fullPluginPath = re.sub(
            "/\/[^\/]+[\/]?$/", "", os.path.dirname(__file__))

        # Standard regex for converting copied files paths
        self.relativePathRegExp = "^((\.\.\/){1,2})(.*content\/)?(\d+|editor)\/(.+)$"

        self.librariesJsonData = None
        self.contentJsonData = None
        self.mainJsonData = None

        # Map flags to string
        disable = {
            self.DISABLE_FRAME: self.DISPLAY_OPTION_FRAME,
            self.DISABLE_DOWNLOAD: self.DISPLAY_OPTION_DOWNLOAD,
            self.DISABLE_EMBED: self.DISPLAY_OPTION_EMBED,
            self.DISABLE_COPYRIGHT: self.DISPLAY_OPTION_COPYRIGHT
        }

    ##
    # Save content and clear cache.
    ##
    def saveContent(self, content, contentMainId=None):
        if "id" in content:
            self.h5pF.updateContent(content, contentMainId)
        else:
            content["id"] = self.h5pF.insertContent(content, contentMainId)

        # Some user data for content has to be reset when the content changes.
        self.h5pF.resetContentUserData(
            contentMainId if contentMainId else content["id"])

        return content["id"]

    ##
    # Load content.
    ##
    def loadContent(self, pid):
        content = self.h5pF.loadContent(pid)

        if content != None:
            content["library"] = {
                "contentId": pid,
                "id": content["library_id"],
                "name": content["library_name"],
                "majorVersion": content["library_major_version"],
                "minorVersion": content["library_minor_version"],
                "embedTypes": content["library_embed_types"],
                "fullscreen": content["library_fullscreen"]
            }
            del content["library_id"], content["library_name"], content[
                "library_embed_types"], content["library_fullscreen"]

            # TODO: Move to filterParameters ?
        return content

    ##
    # Filter content run parameters, rebuild content dependency cache and export file.
    ##
    def filterParameters(self, content):
        print(str(content) + '\n')
        #if not empty(content["filtered"]) and (not self.exportEnabled or (content["slug"] and self.fs.hasExport(content["slug"] + "-" + content["id"] + ".h5p"))):
        #    return content["filtered"]

        # Validate and filter against main library semantics.
        validator = H5PContentValidator(self.h5pF, self)
        params = {
            "library": self.libraryToString(content["library"]),
            "params": json.loads(content["params"])
        }

        if not 'params' in params:
            return None

        validator.validateLibrary(params, {"options": params['library']})

        params = json.dumps(params['params'])

        # Update content dependencies
        content["dependencies"] = validator.getDependencies()
        print("Content dep: " + str(content["dependencies"]) + '\n')
        # Sometimes the parameters are filtered before content has been
        # created
        if content["id"]:
            self.h5pF.deleteLibraryUsage(content["id"])
            self.h5pF.saveLibraryUsage(
                content["id"], content["dependencies"])

            if not content["slug"]:
                content["slug"] = self.generateContentSlug(content)

                # Remove old export file
                self.fs.deleteExport(content["id"] + ".h5p")

            if self.exportEnabled:
                # Recreate export file
                exporter = H5PExport(self.h5pF, self)
                exporter.createExportFile(content)

            # Cache.
            self.h5pF.updateContentFields(content["id"], {
                "filtered": params,
                "slug": content["slug"]
            })
        return params

    ##
    # Generate content slug
    ##
    def generateContentSlug(self, content):
        slug = slugify(content["title"])

        available = None
        while not available:
            if available == False:
                # If not available, add number suffix.
                matches = re.search("(.+-)([0-9]+)$", slug)
                if matches:
                    slug = matches.group(1) + str(int(matches.group(2)) + 1)
                else:
                    slug = slug + "-2"

            available = self.h5pF.isContentSlugAvailable(slug)
        return slug

    ##
    # Find the files required for self content to work.
    ##
    def loadContentDependencies(self, pid, ptype=None):
        dependencies = self.h5pF.loadContentDependencies(pid, ptype)
        
        if self.development_mode and H5PDevelopment.MODE_LIBRARY:
            developmentLibraries = self.h5pD.getLibraries()

            for key, dependency in dependencies.items():
                libraryString = self.libraryToString(dependency)
                if libraryString in developmentLibraries:
                    developmentLibraries[libraryString]["dependencyType"] = dependencies[
                        key]["dependencyType"]
                    dependencies[key] = developmentLibraries[libraryString]

        return dependencies

    ##
    # Get all dependency assets of the given type
    ##
    def getDependencyAssets(self, dependency, ptype, assets, prefix=""):
        # Check if dependency has any files of his type
        if empty(dependency[ptype]) or dependency[ptype][0] == "":
            return

        # Check if we should skip CSS.
        if ptype == "preloadedCss" and "dropLibraryCss" in dependency and dependency["dropLibraryCss"] == "1":
            return

        for f in dependency[ptype]:
            assets.append({
                "path": str(prefix + dependency["path"] + "/" + f.strip(' u\' ')),
                "version": dependency["version"]
            })

        return assets

    ##
    # Combines path with cache buster / version.
    ##
    def getAssetsUrls(self, assets):
        urls = list()
        for asset in assets:
            url = asset['path']

            # Add URL prefix if not external
            if not '://' in asset['path']:
                url = 'uploads/h5pp' + url

            # Add version/cache buster if set
            if 'version' in asset:
                url = url + asset['version']

            urls.append(url)

        return urls

    ##
    # Return file paths for all dependencies files.
    ##
    def getDependenciesFiles(self, dependencies, prefix=""):
        # Build files list for assets
        files = {
            "scripts": [],
            "styles": []
        }

        key = None

        # Avoid caching empty files
        if len(dependencies) == 0:
            return files

        if self.aggregateAssets:
            # Get aggregated files for assets
            key = self.getDependenciesHash(dependencies)
            cachedAssets = self.fs.getCachedAssets(key)
            if cachedAssets != None:
                return dict(files, **cachedAssets)  # Using cached assets

        # Using content dependencies
        for key, dependency in dependencies.items():
            if not 'path' in dependency:
                dependency['path'] = 'libraries/' + \
                    self.libraryToString(dependency, True)
                dependency['preloadedJs'] = dependency[
                    'preloaded_js'].strip('[]').split(',')
                dependency['preloadedCss'] = dependency[
                    'preloaded_css'].strip('[]').split(',')

            dependency['version'] = '?ver=' + str(dependency['major_version']) + \
                '.' + str(dependency["minor_version"]) + \
                '.' + str(dependency["patch_version"])

            scripts = self.getDependencyAssets(
                dependency, "preloadedJs", files["scripts"], prefix)

            if scripts != None:
                files["scripts"] = scripts

            styles = self.getDependencyAssets(
                dependency, "preloadedCss", files["styles"], prefix)

            if styles != None:
                files["styles"] = styles

        if self.aggregateAssets:
            # Aggregate and store assets
            self.fs.cacheAssets(files, key)

            # Keep track of which libraries have been cached in case they
            # are updated
            self.h5pF.saveCachedAssets(key, dependencies)

        return files

    def getDependenciesHash(self, dependencies):
        toHash = list()
        # Use unique identifier for each library version
        for dep, lib in dependencies.items():
            toHash.append(lib["machineName"] + "-" + str(lib["majorVersion"]) +
                        "." + str(lib["minorVersion"]) + "." + str(lib["patchVersion"]))

        # Sort in case the same dependencies comes in a different order
        toHash.sort()

        # Calculate hash sum
        h = hashlib.sha1()
        h.update(''.join([str(i) for i in toHash]))
        return h.hexdigest()

    ##
    # Load library semantics.
    ##
    def loadLibrarySemantics(self, name, majorVersion, minorVersion):
        semantics = None
        if self.development_mode and H5PDevelopment.MODE_LIBRARY:
            # Try to load from dev lib
            semantics = self.h5pD.getSemantics(
                name, majorVersion, minorVersion)

        if semantics == None:
            # Try to load from DB.
            semantics = self.h5pF.loadLibrarySemantics(
                name, majorVersion, minorVersion)

        if semantics != None:
            semantics = json.loads(semantics['semantics'])

        return semantics

    ##
    # Load library
    ##
    def loadLibrary(self, name, majorVersion, minorVersion):
        library = None
        if self.development_mode and H5PDevelopment.MODE_LIBRARY:
            # Try to load from dev
            library = self.h5pD.getLibrary(
                name, majorVersion, minorVersion)
            if library != None:
                library["semantics"] = self.h5pD.getSemantics(
                    name, majorVersion, minorVersion)
        if library == None:
            # Try to load from DB
            library = self.h5pF.loadLibrary(
                name, majorVersion, minorVersion)

        return library

    ##
    # Deletes a library
    ##
    def deleteLibrary(libraryId):
        self.h5pF.deleteLibrary(libraryId)

    ##
    # Recursive. Goes through the dependency tree for the given library and
    # adds all the dependencies to the given array in a flat format.
    ##
    def findLibraryDependencies(self, dependencies, library, nextWeight=0, editor=False):
        for ptype in ["dynamic", "preloaded", "editor"]:
            pproperty = ptype + "Dependencies"
            if not pproperty in library:
                continue  # Skip, no such dependencies

            if ptype == "preloaded" and editor == True:
                # All preloaded dependencies of an editor library is set to
                # editor.
                ptype = "editor"

            for dependency in library[pproperty]:
                dependencyKey = ptype + "-" + dependency["machineName"]
                if dependencyKey in dependencies:
                    continue  # Skip, already have self

                dependencyLibrary = self.loadLibrary(dependency["machineName"], dependency[
                                                    "majorVersion"], dependency["minorVersion"])
                if dependencyLibrary:
                    dependencies[dependencyKey] = {
                        "library": dependencyLibrary,
                        "type": ptype
                    }
                    nextWeight = self.findLibraryDependencies(
                        dependencies, dependencyLibrary, nextWeight, ptype == "editor")
                    nextWeight = nextWeight + 1
                    dependencies[dependencyKey]["weight"] = nextWeight
                else:
                    # self site is missing a dependency !
                    print("Missing dependency %s required by %s" % (
                        libraryToString(dependency), libraryToString(library)))

        return nextWeight

    ##
    # Check if a library is of the version we"re looking for
    #
    # Same version means that the majorVersion and minorVersion is the same
    ##
    def isSameVersion(library, dependency):
        if library["machineName"] != dependency["machineName"]:
            return False
        if library["majorVersion"] != dependency["majorVersion"]:
            return False
        if library["minorVersion"] != dependency["minorVersion"]:
            return False
        return True

    ##
    # Recursive function for removing directories.
    ##
    def deleteFileTree(self, pdir):
        if not os.path.isdir(pdir):
            return False

        files = list(set(os.listdir(pdir)).difference([".", ".."]))

        for f in files:
            self.deleteFileTree(pdir + "/" + f) if os.path.isdir(pdir +
                                                                "/" + f) else os.remove(pdir + "/" + f)

        return os.rmdir(pdir)

    ##
    # Writes library data as string on the form {machineName} {majorVersion}.{minorVersion}
    ##
    def libraryToString(self, library, folderName=False):
        if 'machineName' in library:
            return library["machineName"] + ("-" if folderName else " ") + str(library["majorVersion"]) + "." + str(library["minorVersion"])
        elif 'machine_name' in library:
            return library["machine_name"] + ("-" if folderName else " ") + str(library["major_version"]) + "." + str(library["minor_version"])
        else:
            return library["name"] + ("-" if folderName else " ") + str(library["majorVersion"]) + "." + str(library["minorVersion"])

    ##
    # Parses library data from a string on the form {machineName} {majorVersion}.{minorVersion}
    ##
    def libraryFromString(self, libraryString):
        pre = "^([\w0-9\-\.]{1,255})[\-\ ]([0-9]{1,5})\.([0-9]{1,5})$"
        res = re.search(pre, libraryString)
        if res:
            return {
                "machineName": res.group(1),
                "majorVersion": res.group(2),
                "minorVersion": res.group(3)
            }
        return False

    ##
    # Determine the correct embed type to use.
    ##
    def determineEmbedType(self, contentEmbedType, libraryEmbedTypes):
        # Detect content embed type
        embedType = "div" if (
            "div" in libraryEmbedTypes.lower()) else "iframe"

        if libraryEmbedTypes != None and libraryEmbedTypes != "":
            # Check that embed type is available for library
            if (embedType in embedTypes) == False:
                # Not available, pick default.
                embedType = "div" if (
                    "div" in embedTypes) != False else "iframe"

        return embedType

    ##
    # Get the absolute version for the library as a human readable string.
    ##
    def libraryVersion(library):
        return library.major_version + "." + library.minor_version + "." + library.patch_version

    ##
    # Determine which version content with the given library can be upgraded to.
    ##
    def getUpgrades(library, versions):
        for upgrade in versions:
            if (upgrade.major_version > library.major_version) or ((upgrade.major_version == library.major_version) and (upgrade.minor_version > library.minor_version)):
                upgrades[upgrade.id] = libraryVersion(upgrade)

        return upgrades

    ##
    # Converts all the properties of the given object or array from
    # snake_case to camelCase. Useful after fetching data from the database.
    #
    # Note that some databases does not support camelCase.
    ##
    def snakeToCamel(self, arr, obj=False):
        for key, val in arr:
            next = -1
            while next != False:
                next = key.find("_", next + 1)
                key = substr_replace(key, key[next + 1].upper(), next, 2)

            newArr[key] = val

        return newArr if obj else newArr

    ##
    # Get a list of installed libraries, different minor version will
    # return a separate entries.
    ##
    def getLibrariesInstalled(self):
        librariesInstalled = dict()
        libs = self.h5pF.loadLibraries()

        for libName, library in libs.items():
            librariesInstalled[libName + " " + str(library['major_version']) +
                            "." + str(library['minor_version'])] = library['patch_version']

        return librariesInstalled

    ##
    # Easy way to combine similar data sets.
    ##
    def combineArrayValues(self, inputs):
        results = dict()
        for index, values in inputs.items():
            for key, value in values.items():
                results[key] = {index: value}

        return results

    ##
    # Fetch a list of libraries" metadata from h5p.org.
    # save URL tutorial to database. Each platform implementation
    # is responsible for invoking self, eg using cron
    ##
    def fetchLibrariesMetadata(self, fetchingDisabled=False):
        # Gather data
        uuid = self.h5pF.getOption("H5P_UUID", "")
        platform = self.h5pF.getPlatformInfo()
        data = {
            "api_version": 2,
            "uuid": uuid,
            "platform_name": platform["name"],
            "platform_version": platform["version"],
            "h5p_version": platform["h5pVersion"],
            "disabled": 1 if fetchingDisabled else 0,
            "local_id": binascii.crc32(self.fullPluginPath),
            "type": self.h5pF.getOption("H5P_SITETYPE", "local"),
            "num_authors": self.h5pF.getNumAuthors(),
            "libraries": json.dumps({
                "patch": self.getLibrariesInstalled(),
                "content": self.h5pF.getLibraryContentCount(),
                "loaded": self.h5pF.getLibraryStats("library"),
                "created": self.h5pF.getLibraryStats("content create"),
                "createUpload": self.h5pF.getLibraryStats("content create upload"),
                "deleted": self.h5pF.getLibraryStats("content delete"),
                "resultViews": self.h5pF.getLibraryStats("results content"),
                "shortcodeInserts": self.h5pF.getLibraryStats("content shortcode insert")
            })
        }

        # Send request
        result = self.h5pF.fetchExternalData(
            "https://h5p.org/libraries-metadata.json", data)
        if empty(result):
            return

        # Process results
        jsonData = json.loads(result.read())
        if empty(jsonData):
            return

        # Handle libraries metadata
        if 'libraries' in jsonData:
            for machineName, libInfo in jsonData['libraries'].items():
                if 'tutorialUrl' in libInfo:
                    self.h5pF.setLibraryTutorialUrl(
                        machineName, libInfo['tutorialUrl'])

        # Handle new uuid
        if uuid == "" and jsonData['uuid']:
            self.h5pF.setOption("H5P_UUID", jsonData['uuid'])

        # Handle latest version of H5P
        if not empty(jsonData['latest']):
            self.h5pF.setOption("H5P_UPDATE_AVAILABLE", jsonData[
                                'latest']['releasedAt'])
            self.h5pF.setOption("H5P_UPDATE_AVAILABLE_PATH",
                                jsonData['latest']['path'])

    def getGlobalDisable():
        disable = self.DISABLE_NONE

        # Allow global settings to override and disable options
        if not self.h5pF.getOption("frame", True):
            disable = disable | self.DISABLE_FRAME
        else:
            if not self.h5pF.getOption("export", True):
                disable = disable | self.DISABLE_DOWNLOAD
            if not self.h5pF.getOption("embed", True):
                disable = disable | self.DISABLE_EMBED
            if not self.h5pF.getOption("copyright", True):
                disable = disable | self.DISABLE_COPYRIGHT
            if not self.h5pF.getOption("icon", True):
                disable = disable | self.DISABLE_ABOUT

        return disable

    ##
    # Determine disable state from sources.
    ##
    def getDisable(sources, current):
        for bit, option in H5PCore.disable:
            if self.h5pF.getOption("export" if (bit & H5PCore.DISABLE_DOWNLOAD) else option, True):
                if not sources[option] or not sources[option]:
                    current = current | bit  # Disable
                else:
                    current = current & bit  # Enable

        return current

    ##
    # Small helper for getting the library"s ID.
    ##
    def getLibraryId(self, library, libString=None):
        global libraryIdMap

        if not libString:
            libString = self.libraryToString(library)
        
        if not libString in libraryIdMap or libraryIdMap[libString] is None:
            libraryIdMap[libString] = self.h5pF.getLibraryId(
                library["machineName"], library["majorVersion"], library["minorVersion"])

        return libraryIdMap[libString]

    ##
    # Makes it easier to print response when AJAX request succeeds.
    ##
    def ajaxSuccess(self, data=None):
        response = {
            "success": True
        }
        if data != None:
            response["data"] = data

        return json.dumps(response)

    ##
    # Makes it easier to print response when AJAX request fails.
    # will exit after printing error.
    ##
    def ajaxError(self, message=None):
        response = {
            "success": False
        }
        if message != None:
            response["message"] = message

        return json.dumps(response)

    ##
    # Print JSON headers with UTF-8 charset and json encode response data.
    # Makes it easier to respond using JSON.
    ##
    def printJson(self, data):
        print("Cache-Control: no-cache\n")
        print("Content-type: application/json; charset=utf-8\n")
        print(json.dumps(data))

    ##
    # Get a new H5P security token for the given action
    ##
    def createToken(self, action):
        timeFactor = self.getTimeFactor()
        h = hashlib.new('md5')
        h.update(action + str(timeFactor) + str(uuid.uuid1()))
        return h.digest()

    ##
    # Create a time based number which is unique for each 12 hour.
    ##
    def getTimeFactor(self):
        return math.ceil(int(time.time()) / (86400 / 2))

##
# Functions for validating basic types from H5P library semantics.
##


class H5PContentValidator:
    allowed_styleable_tags = ["span", "p", "div"]

    ##
    # Constructor for the H5PContentValidator
    ##
    def __init__(self, H5PFramework, H5PCore):
        self.h5pF = H5PFramework
        self.h5pC = H5PCore
        self.typeMap = {
            "text": "validateText",
            "number": "validateNumber",
            "boolean": "validateBoolean",
            "list": "validateList",
            "group": "validateGroup",
            "file": "validateFile",
            "image": "validateImage",
            "video": "validateVideo",
            "audio": "validateAudio",
            "select": "validateSelect",
            "library": "validateLibrary"
        }
        self.nextWeight = 1

        # Keep track of the libraries we load to avoid loading it multiple
        # times.
        self.libraries = dict()

        # Keep track of all dependencies for the given content.
        self.dependencies = dict()

    ##
    # Get the flat dependency tree.
    ##
    def getDependencies(self):
        return self.dependencies

    ##
    # Validate given text value against text semantics.
    ##
    def validateText(self, text, semantics):
        if not isinstance(text, str):
            text = ''

        if 'tags' in semantics:
            tags = ['div', 'span', 'p', 'br'] + semantics['tags']

            if 'table' in tags:
                tags = tags + ['tr', 'td', 'th',
                            'colgroup', 'thead', 'tbody', 'tfoot']
            if 'b' in tags and not 'strong' in tags:
                tags.append('strong')
            if 'i' in tags and not 'em' in tags:
                tags.append('em')
            if 'ul' in tags or 'ol' in tags and not 'li' in tags:
                tags.append('li')
            if 'del' in tags or 'strike' in tags and not 's' in tags:
                tags.append('s')

            stylePatterns = list()
            if 'font' in semantics:
                if 'size' in semantics['font']:
                    stylePatterns.append(
                        '(?i)^font-size: *[0-9.]+(em|px|%) *;?$')
                if 'family' in semantics['font']:
                    stylePatterns.append('(?i)^font-family: *[a-z0-9," ]+;?$')
                if 'color' in semantics['font']:
                    stylePatterns.append(
                        '(?i)^color: *(#[a-f0-9]{3}[a-f0-9]{3}?|rgba?\([0-9, ]+\)) *;?$')
                if 'background' in semantics['font']:
                    stylePatterns.append(
                        '(?i)^background-color: *(#[a-f0-9]{3}[a-f0-9]{3}?|rgba?\([0-9, ]+\)) *;?$')
                if 'spacing' in semantics['font']:
                    stylePatterns.append(
                        '(?i)^letter-spacing: *[0-9.]+(em|px|%) *;?$')
                if 'height' in semantics['font']:
                    stylePatterns.append(
                        '(?i)^line-height: *[0-9.]+(em|px|%|) *;?$')

            stylePatterns.append('(?i)^text-align: *(center|left|right);?$')

            text = self.filterXss(text, tags, stylePatterns)
        else:
            text = html.escape(text, True)

        if 'maxLength' in semantics:
            text = text[0:semantics['maxLength']]

        if not text == '' and 'optional' in semantics and 'regexp' in semantics:
            pattern = semantics['regexp'][
                'modifiers'] if 'modifiers' in semantics['regexp'] else ''
            if not re.search(pattern, text):
                print('Provided string is not valid according to regexp in semantics. (value: %s, regexp: %s)' % (
                    text, pattern))
                text = ''

    ##
    # Validates content files
    ##
    def validateContentFiles(self, contentPath, isLibrary=False):
        if self.h5pC.disableFileCheck == True:
            return True

        # Scan content directory for files, recurse into sub directories.
        files = list(set(os.listdir(contentPath)).difference([".", ".."]))
        valid = True
        whitelist = self.h5pF.getWhitelist(
            isLibrary, H5PCore.defaultContentWhitelist, H5PCore.defaultLibraryWhitelistExtras)

        wl_regex = "^.*\.(" + re.sub(" ", "|", whitelist) + ")$"

        for f in files:
            filePath = contentPath + "/" + f
            if os.path.isdir(filePath):
                valid = self.validateContentFiles(
                    filePath, isLibrary) and valid
            else:
                if not re.search(wl_regex, f.lower()):
                    print(
                        "File \"%s\" not allowed. Only files with the following extension are allowed : %s" % (f, whitelist))
                    valid = False

        return valid

    ##
    # Validate given value against number semantics
    ##
    def validateNumber(self, number, semantics):
        # Validate that number is indeed a number
        if not isinstance(number, int):
            number = 0

        # Check if number is within valid bounds. Move withing bounds if not.
        if 'min' in semantics and number < semantics['min']:
            number = semantics['min']
        if 'max' in semantics and number > semantics['max']:
            number = semantics['max']

        # Check if number if withing allowed bounds even if step value is set.
        if 'step' in semantics:
            textNumber = number - \
                (semantics['min'] if 'min' in semantics else 0)
            rest = textNumber % semantics['step']
            if rest != 0:
                number = number - rest

        # Check if number has proper number of decimals.
        if 'decimals' in semantics:
            number = round(number, semantics['decimals'])

    ##
    # Validate given value against boolean semantics
    ##
    def validateBoolean(self, boolean, semantics):
        return isinstance(boolean, bool)

    ##
    # Validate select values
    ##
    def validateSelect(self, select, semantics):
        optional = semantics['optional'] if 'optional' in semantics else False
        strict = False
        if 'options' in semantics and not empty(semantics['options']):
            # We have a strict set of options to choose from.
            strict = True
            options = dict()
            for option in semantics['options']:
                options[option['value']] = True

        if 'multiple' in semantics and semantics['multiple']:
            # Multi-choice generates array of values. Test each one against valid
            # options, if we are strict. First make sure we are working on an
            # array.
            if not isinstance(select, list):
                select = list(select)

            for key, value in select:
                if strict and not optional and not options[value]:
                    print(
                        "Invalid selected option in multi-select.")
                    del select[key]
                else:
                    select[key] = html.escape(value, True)
        else:
            # Single mode. If we get an array in here, we chop off the first
            # element and use that instead.
            if isinstance(select, list):
                select = select[0]

            if strict and not optional and not options[select]:
                print(
                    "Invalid selected option in select.")
                select = semantics[options[0]['value']]

            select = html.escape(select, True)

    ##
    # Validate given list value against list semantics.
    # Will recurse into validating each item in the list according to the type.
    ##
    def validateList(self, plist, semantics):
        field = semantics
        function = self.typeMap[field['type']]

        if not isinstance(plist, list):
            plist = list()

        # Validate each element in list.
        for value in plist:
            eval('self.' + function + '(value, field)')

        if len(plist) == 0:
            plist = None

    ##
    # Validate a file like object, such as video, image, audio and file.
    ##
    def validateFilelike(self, f, semantics, typeValidKeys=[]):
        # Do not allow to use files from other content folders.
        matches = re.search(self.h5pC.relativePathRegExp, f['path'])
        if matches:
            f['path'] = matches.group(4)

        # Make sure path and mime does not have any special chars
        f['path'] = html.escape(f['path'], True)
        if 'mime' in f:
            f['mime'] = html.escape(f['mime'], True)

        # Remove attributes that should not exist, they may contain JSON escape
        # code.
        validKeys = ["path", "mime", "copyright"] + typeValidKeys
        if 'extraAttributes' in semantics:
            validKeys = validKeys + semantics['extraAttributes']

        self.filterParams(f, validKeys)

        if 'width' in f:
            f['width'] = int(f['width'])

        if 'height' in f:
            f['height'] = int(f['height'])

        if 'codecs' in f:
            f['codecs'] = html.escape(f['codecs'], True)

        if 'quality' in f:
            if not isinstance(f['quality'], object) or not 'level' in f['quality'] or not 'label' in f['quality']:
                del f['quality']
            else:
                self.filterParams(f['quality'], ["level", "label"])
                f['quality']['level'] = int(f['quality']['level'])
                f['quality']['label'] = html.escape(f['equality']['label'], True)

        if 'copyright' in f:
            self.validateGroup(f['copyright'], self.getCopyrightSemantics())

    ##
    # Validate given file data
    ##
    def validateFile(self, f, semantics):
        self.validateFilelike(f, semantics)

    ##
    # Validate given image data
    ##
    def validateImage(self, image, semantics):
        self.validateFilelike(
            image, semantics, ["width", "height", "originalImage"])

    ##
    # Validate given video data
    ##
    def validateVideo(self, video, semantics):
        for variant in video:
            self.validateFilelike(variant, semantics, [
                                "width", "height", "codecs", "quality"])

    ##
    # Validate given audio data
    ##
    def validateAudio(self, audio, semantics):
        for variant in audio:
            self.validateFilelike(variant, semantics)

    ##
    # Validate given group value against group semantics
    ##
    def validateGroup(self, group, semantics, flatten=True):
        # Groups with just one field are compressed in the editor to only output
        # the child content. (Exemption for fake groups created by
        # "validateBySemantics" above)
        function = None
        field = None
        isSubContent = True if 'isSubContent' in semantics and semantics[
            'isSubContent'] == True else False

        if len(semantics['fields']) == 1 and flatten and not isSubContent:
            field = semantics['fields'][0]
            function = self.typeMap[field['type']]
            eval('self.' + function + '(group, field)')
        else:
            for key, value in group.items():
                if isSubContent and key == 'subContentId':
                    continue

                found = False
                for field in semantics['fields']:
                    if field['name'] == key:
                        if 'optional' in semantics:
                            field['optional'] = True
                        function = self.typeMap[field['type']]
                        found = True
                        break
                if found:
                    if function:
                        eval('self.' + function + '(value, field)')
                        if value == None:
                            del(key)
                    else:
                        print('H5P internal error: unknown content type "%s" in semantics. Removing content !' % field['type'])
                        del(key)
                else:
                    del(key)

        if not 'optional' in semantics:
            if group == None:
                return

            for field in semantics['fields']:
                if not 'optional' in field:
                    if not hasattr(group, field['name']):
                        continue
                        #No message for the moment

    ##
    # Validate given library value against library semantics.
    # Check if provided library is withing allowed options.
    #
    # Will recurse into validating the library"s semantics too.
    ##

    def validateLibrary(self, value, semantics):
        if not 'library' in value:
            value = None
            return

        if not value['library'] in semantics['options']:
            message = None
            machineNameArray = value['library'].split(' ')
            machineName = machineNameArray[0]
            for semanticsLibrary in semantics['options']:
                semanticsMachineNameArray = semanticsLibrary.split(' ')
                semanticsMachineName = semanticsMachineNameArray[0]
                if machineName == semanticsMachineName:
                    message = 'The version of the H5P library %s used in the content is not valid. Content contains %s, but it should be %s.' % (
                        machineName, value['library'], semanticsLibrary)

            if message == None:
                message = 'The H5P library %s used in the content is not valid.' % value[
                    'library']
                print(message)
                value = None
                return

        if not value['library'] in self.libraries:
            libSpec = self.h5pC.libraryFromString(value['library'])
            library = self.h5pC.loadLibrary(libSpec['machineName'], libSpec[
                                            'majorVersion'], libSpec['minorVersion'])
            library['semantics'] = self.h5pC.loadLibrarySemantics(
                libSpec['machineName'], libSpec['majorVersion'], libSpec['minorVersion'])
            self.libraries[value['library']] = library
        else:
            library = self.libraries[value['library']]

        self.validateGroup(value['params'], {
            'type': 'group',
            'fields': library['semantics'],
        }, False)
        validKeys = ['library', 'params', 'subContentId']
        if 'extraAttributes' in semantics:
            validKeys = validKeys + semantics['extraAttributes']
        self.filterParams(value, validKeys)

        if 'subContentId' in value and not re.search('(?i)^\{?[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\}?$', value['subContentId']):
            del(value['subContentId'])

        depKey = 'preloaded-' + library['machine_name']
        if not depKey in self.dependencies:
            self.dependencies[depKey] = {
                'library': library,
                'type': 'preloaded'
            }
            self.nextWeight = self.h5pC.findLibraryDependencies(
                self.dependencies, library, self.nextWeight)
            self.nextWeight = self.nextWeight + 1
            self.dependencies[depKey]['weight'] = self.nextWeight

    ##
    # Check params for a whitelist of allowed properties
    ##
    def filterParams(self, params, whitelist):
        for key, value in params.items():
            if not key in whitelist:
                del params[key]

    ##
    # Prevent cross-site-scripting (XSS) vulnerabilities
    ##
    def filterXss(self, string, allowedTags=['a', 'em', 'strong', 'cite', 'blockquote', 'code', 'ul', 'ol', 'li', 'dl', 'dt', 'dd'], allowedStyles=False):
        if len(string) == 0:
            return string

        # Only operate on valid UTF-8 strings
        if not re.search('(?us)^.', string):
            return ''

        self.allowedStyles = allowedStyles
        # Store the text format
        self.filterXssSplit(allowedTags, True)
        # Remove NULL characters (ignored by some browsers)
        string = string.replace(chr(0), '')
        # Remove Netscape 4 JS entities
        string = re.sub('%&\s*\{[^}]*(\)\s*;?|$)%', '', string)

        # Defuse all HTML entities
        string = string.replace('&', '&amp;')
        # Change back only well-formed entities in our whitelist
        # Deciman numeric entities
        string = re.sub('&amp;#([0-9]+;)', '&#\1', string)
        # Hexadecimal numeric entities
        string = re.sub('&amp;#[Xx]0*((?:[0-9A-Fa-f]{2})+;)', '&#x\1', string)
        # Named entities
        string = re.sub('&amp;([A-Za-z][A-Za-z0-9]*;)', '&\1', string)

        return re.sub('%(<(?=[^a-zA-Z!/])|<!--.*?-->|<[^>]*(>|$)|>)%x', self.filterXssSplit, string)

    ##
    # Process an HTML tag
    ##
    def filterXssSplit(self, m, store=False):
        if store:
            self.allowedHtml = m
            return self.allowedHtml

        string = m[1]

        if string[0:1] != '<':
            # We matched a lone ">" character
            return '&gt;'
        elif len(string) == 1:
            # We matched a lone "<" character
            return '&lt;'

        matches = re.search('%^<\s*(/\s*)?([a-zA-Z0-9\-]+)([^>]*)>?|(<!--.*?-->)$%', string)
        if not matches:
            # Seriously malformed
            return ''

        slash = matches.group(0).strip()
        elem = matches.group(1)
        attrList = matches.group(2)
        comment = matches.group(3)

        if comment:
            elem = '!--'

        if not elem.lower() in self.allowedHtml:
            # Disallowed HTML element
            return ''

        if comment:
            return comment

        if slash != '':
            return '</' + elem + '>'

        # Is there a closing XHTML slash at the end of the attributes ?
        attrList = re.sub('%(\s?)/\s*$%', '\1', attrList, -1)
        xhtmlSlash = '/' if attrList else ''

        # Clean up attributes
        attr2 = ' '.join(self.filterXssAttributes(attrList, self.allowedStyles if elem in self.allowed_styleable_tags else False))
        attr2 = re.sub('[<>]', '', attr2)
        attr2 = ' ' + attr2 if len(attr2) else ''

        return '<' + elem + attr2 + xhtmlSlash + '>'


    def getCopyrightSemantics(self):
        semantics = {
            "name": "copyright",
            "type": "group",
            "label": "Copyright information",
            "fields": [
                {
                    "name": "title",
                    "type": "text",
                    "label": "Title",
                    "placeholder": "La Gioconda",
                    "optional": 'true'
                },
                {
                    "name": "author",
                    "type": "text",
                    "label": "Author",
                    "placeholder": "Leonardo da Vinci",
                    "optional": 'true'
                },
                {
                    "name": "year",
                    "type": "text",
                    "label": "Year(s)",
                    "placeholder": "1503 - 1517",
                    "optional": 'true'
                },
                {
                    "name": "source",
                    "type": "text",
                    "label": "Source",
                    "placeholder": "http://en.wikipedia.org/wiki/Mona_Lisa",
                    "optional": 'true',
                    "regexp": {
                        "pattern": "^http[s]?://.+",
                        "modifiers": "i"
                    }
                },
                {
                    "name": "license",
                    "type": "select",
                    "label": "License",
                    "default": "U",
                    "options": [
                        {
                            "value": "U",
                            "label": "Undisclosed"
                        },
                        {
                            "value": "CC BY",
                            "label": "Attribution 4.0"
                        },
                        {
                            "value": "CC BY-SA",
                            "label": "Attribution-ShareAlike 4.0"
                        },
                        {
                            "value": "CC BY-ND",
                            "label": "Attribution-NoDerivs 4.0"
                        },
                        {
                            "value": "CC BY-NC",
                            "label": "Attribution-NonCommercial 4.0"
                        },
                        {
                            "value": "CC BY-NC-SA",
                            "label": "Attribution-NonCommercial-ShareAlike 4.0"
                        },
                        {
                            "value": "CC BY-NC-ND",
                            "label": "Attribution-NonCommercial-NoDerivs 4.0"
                        },
                        {
                            "value": "GNU GPL",
                            "label": "General Public License v3"
                        },
                        {
                            "value": "PD",
                            "label": "Public Domain"
                        },
                        {
                            "value": "ODC PDDL",
                            "label": "Public Domain Dedication and Licence"
                        },
                        {
                            "value": "CC PDM",
                            "label": "Public Domain Mark"
                        },
                        {
                            "value": "C",
                            "label": "Copyright"
                        }
                    ]
                }
            ]
        }
        
        return semantics
