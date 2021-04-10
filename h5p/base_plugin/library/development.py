# -*-coding:Latin-1 -*

import os
import re
import cgi
import json
import glob
import pprint
import hashlib
import zipfile

is_array = lambda var: isinstance(var, (list, tuple))

def empty(variable):
    if not variable:
        return True
    return False

def isset(variable):
    return variable in locals() or variable in globals()

def substr_replace(subject, replace, start, length):
    if length == None:
        return subject[:start] + replace
    elif length < 0:
        return subject[:start] + replace + subject[length:]
    else:
        return subject[:start] + replace + subject[start + length:]

def mb_substr(s, start, length=None, encoding="UTF-8"):
    u_s = s.decode(encoding)
    return (u_s[start:(start + length)] if length else u_s[start:]).encode(encoding)

##
# This is a data which uses the file system so it isn't specific to any framework.
##


class H5PDevelopment:

    MODE_NONE = 0
    MODE_CONTENT = 1
    MODE_LIBRARY = 2

    ##
    # Constructor of H5PDevelopment
    ##
    def __init__(self, H5PFramework, filesPath, language, libraries=None):
        self.h5pF = H5PFramework
        self.language = language
        self.filesPath = filesPath
        if libraries != None:
            self.libraries = libraries
        else:
            self.findLibraries(filesPath + '/development')

    ##
    # Get contents of file.
    ##
    def getFileContents(f):
        if os.path.exists(f) == False:
            return None

        contents = open(f).read(1000)
        if contents == False:
            return None

        return contents

    ##
    # Scans development directory and fin all libraries.
    ##
    def findLibraries(path):
        self.libraries = []

        if os.path.isdir(path) == False:
            return

        contents = os.listdir(path)

        for i in contents:
            if i[0] == '.':
                continue  # Skip hidden stuff.

            libraryPath = path + '/' + i
            libraryJSON = self.getFileContents(
                libraryPath + '/' + '/library.json')
            if libraryJSON == None:
                continue  # No JSON file, skip.

            library = json.loads(libraryJSON)
            if library == None:
                continue  # Invalid JSON.

            # Save/update library.
            library['libraryId'] = self.h5pF.getLibraryId(library['machineName'], library['majorVersion'], library['minorVersion'])
            self.h5pF.saveLibraryData(library, library['libraryId'] == False)

            library['path'] = 'development/' + i
            self.libraries[H5PDevelopment.libraryToString(library['machineName'], library['majorVersion'], library['minorVersion'])] = library

            # Go trough libraries and insert dependencies. Missing deps. Will
            # just be ignored and not available.
            self.h5pF.lockDependencyStorage()
            for library in self.libraries:
                self.h5pF.deleteLibraryDependencies(library['libraryId'])
                # This isn't optimal, but without it we would get duplicate
                # warnings.
                types = ['preloaded', 'dynamic', 'editor']
                for dtype in types:
                    if isset(library[dtype + 'Dependencies']):
                        self.h5pF.saveLibraryDependencies(library['libraryId'], library[dtype + 'Dependencies'], dtype)

            self.h5pF.unlockDependencyStorage()

        def getLibraries():
            return self.libraries

        ##
        # Get library
        ##
        def getLibrary(name, majorVersion, minorVersion):
            library = H5PDevelopment.libraryToString(
                name, majorVersion, minorVersion)
            return self.libraries[library] if isset(self.libraries[library]) == True else None

        ##
        # Get semantics for the given library.
        ##
        def getSemantics(name, majorVersion, minorVersion):
            library = H5PDevelopment.libraryToString(
                name, majorVersion, minorVersion)
            if isset(self.libraries[library]) == False:
                return None

            return self.getFileContents(self.filesPath + self.libraries[library]['path'] + '/semantics.json')

        ##
        # Get translations for the given library
        ##
        def getLanguage(name, majorVersion, minorVersion, language):
            library = H5PDevelopment.libraryToString(
                name, majorVersion, minorVersion)
            if isset(self.libraries[library]) == False:
                return None

            return self.getFileContents(self.filesPath + self.libraries[library]['path'] + '/language/' + language + '.json')

        ##
        # Writes library as string on the form 'name majorVersion.minorVersion'
        ##
        def libraryToString(name, majorVersion, minorVersion):
            return name + ' ' + majorVersion + '.' + minorVersion
