# -*-coding:Latin-1 -*

import os
import re
import cgi
import json
import glob
import uuid
import pprint
import shutil
import hashlib
import zipfile
from django.conf import settings

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
# The default file storage class for H5P.
##
class H5PDefaultStorage:
    ##
    # Constructor for H5PDefaultStorage
    ##
    def __init__(self, path):
        self.path = path

    ##
    # Store the library folder.
    ##
    def saveLibrary(self, library):
        dest = os.path.join(self.path, 'libraries',
                            self.libraryToString(library, True))

        # Make sure destination dir doesn't exist
        self.deleteFileTree(dest)

        # Move library folder
        self.copyFileTree(library['uploadDirectory'], dest)

    ##
    # Store the content folder.
    ##
    def saveContent(self, source, pid):
        dest = os.path.join(self.path, 'content', str(pid))
        # Remove any old content
        self.deleteFileTree(dest)

        self.copyFileTree(source, dest)

        return True

    ##
    # Remove content folder.
    ##
    def deleteContent(self, pid):
        self.deleteFileTree(os.path.join(self.path, 'content', str(pid)))

    ##
    # Creates a stored copy of the content folder.
    ##
    def cloneContent(self, pid, newId):
        path = os.path.join(self.path, 'content')
        self.copyFileTree(os.path.join(path, pid), os.path.join(path, newId))

    ##
    # Get path to a new unique tmp folder.
    ##
    def getTmpPath(self):
        temp = os.path.join(self.path, 'tmp')
        self.dirReady(temp)
        return os.path.join(temp, str(uuid.uuid1()))

    ##
    # Fetch content folder and save in target directory.
    ##
    def exportContent(self, pid, target):
        self.copyFileTree(os.path.join(self.path, 'content', pid), target)

    ##
    # Fetch library folder and save in target directory.
    ##
    def exportLibrary(self, library, target, developmentPath=None):
        folder = self.libraryToString(library, True)
        srcPath = os.path.join(
            'libraries', folder if developmentPath == None else developmentPath)
        self.copyFileTree(os.path.join(self.path, srcPath),
                        os.path.join(target, folder))

    ##
    # Save export in file system
    ##
    def saveExport(self, source, filename):
        self.deleteExport(filename)

        if not self.dirReady(os.path.join(self.path, 'exports')):
            raise Exception('Unable to create directory for H5P export file.')

        try:
            shutil.copy(source, os.path.join(self.path, 'exports', filename))
        except IOError as e:
            print('Unable to copy %s' % e)

        return True

    ##
    # Remove given export file.
    ##
    def deleteExport(self, filename):
        target = os.path.join(self.path, 'exports', filename)
        if os.path.exists(target):
            os.remove(target)

    ##
    # Check if the given export file exists.
    ##
    def hasExport(self, filename):
        target = os.path.join(self.path, 'exports', filename)
        return os.path.exists(target)

    ##
    # Will concatenate all JavaScripts and Stylesheets into two files in order
    # to improve page performance.
    ##
    def cacheAssets(self, files, key):

        for dtype, assets in files.iteritems():
            if empty(assets):
                continue  # Skip no assets

            content = ''
            for asset in assets:
                # Get content form asset file
                assetContent = open(self.path + asset['path']).read()
                cssRelPath = re.sub('/[^\/]+$/', '', asset['path'])

                # Get file content and concatenate
                if dtype == 'scripts':
                    content = content + assetContent + ';\n'
                else:
                    # Rewrite relative URLs used inside Stylesheets
                    content = content + re.sub('/url\([\'"]?([^"\')]+)[\'"]?\)/i', lambda matches:
                                            matches[0] if re.search('/^(data:|([a-z0-9]+:)?\/)/i', matches[1] == 1) else 'url("../' + cssRelPath + matches[1] + '")', assetContent) + '\n'

            self.dirReady(os.path.join(self.path, 'cachedassets'))
            ext = 'js' if dtype == 'scripts' else 'css'
            outputfile = '/cachedassets/' + key + '.' + ext

            with open(self.path + outputfile, 'w') as f:
                f.write(content)
            files[dtype] = [{
                'path': outputfile,
                'version': ''
            }]

    ##
    # Will check if there are cache assets available for content.
    ##
    def getCachedAssets(self, key):
        files = {
            'scripts': [],
            'styles': []
        }
        js = '/cachedassets/' + key + '.js'
        if os.path.exists(self.path + js):
            files['scripts'].append({
                'path': js,
                'version': ''
            })

        css = '/cachedassets/' + key + '.css'
        if os.path.exists(self.path + css):
            files['styles'].append({
                'path': css,
                'version': ''
            })

        return None if empty(files) else files

    ##
    # Remove the aggregated cache files.
    ##
    def deleteCachedAssets(self, keys):
        for hhash in keys:
            for ext in ['js', 'css']:
                path = os.path.join(self.path, 'cachedassets', hhash, ext)
                if os.path.exists(path):
                    os.remove(path)

    ##
    # Recursive function for copying directories.
    ##
    def copyFileTree(self, source, destination):
        if not self.dirReady(destination):
            raise Exception('Unable to copy')

        for f in os.listdir(source):
            if (f != '.') and (f != '..') and f != '.git' and f != '.gitignore':
                if os.path.isdir(os.path.join(source, f)):
                    self.copyFileTree(os.path.join(source, f),
                                    os.path.join(destination, f))
                else:
                    shutil.copy(os.path.join(source, f),
                                os.path.join(destination, f))

    ##
    # Recursive function that makes sure the specified directory exists and
    # is writable.
    ##
    def dirReady(self, path):
        if not os.path.exists(path):
            parent = re.sub('\/[^\/]+\/?$', '', path)
            if not self.dirReady(parent):
                return False

            os.mkdir(path, 0o777)

        if not os.path.isdir(path):
            raise Exception('Path is not a directory')
            return False

        if not os.access(path, os.W_OK):
            raise Exception(
                'Unable to write to %s - check directory permissions -' % path)
            return False

        return True

    ##
    # Writes library data as string on the form {machineName} {majorVersion}.{minorVersion}
    ##
    def libraryToString(self, library, folderName=False):
        if 'machine_name' in library:
            return library['machine_name'] + ('-' if folderName else ' ') + str(library['major_version']) + '.' + str(library['minor_version'])
        else:
            return library['machineName'] + ('-' if folderName else ' ') + str(library['majorVersion']) + '.' + str(library['minorVersion'])

    ##
    # Recursive function for removing directories.
    ##
    def deleteFileTree(self, pdir):
        if not os.path.isdir(pdir):
            return False

        files = list(set(os.listdir(pdir)).difference(['.', '..']))

        for f in files:
            self.deleteFileTree(os.path.join(pdir, f)) if os.path.isdir(
                os.path.join(pdir, f)) else os.remove(os.path.join(pdir, f))

        return os.rmdir(pdir)

    ##
    # Save files uploaded through the editor.
    ##
    def saveFile(self, files, contentid, pid=None):
        filedata = files.getData()
        path = os.path.join(settings.MEDIA_ROOT, 'h5pp')
        if filedata != None and contentid == '0':
            path = os.path.join(path, 'editor', files.getType() + 's')
            if not os.path.exists(path):
                os.makedirs(path)
            with open(os.path.join(path, files.getName()), 'w+') as f:
                f.write(filedata)
        elif filedata != None and contentid != '0':
            path = os.path.join(path, 'content', str(
                contentid), files.getType() + 's')
            if not os.path.exists(path):
                os.makedirs(path)
            with open(os.path.join(path, files.getName()), 'w+') as f:
                f.write(filedata)
        elif contentid == '0':
            path = os.path.join(path, 'editor', files.getType() + 's')
            content = files.getFile()
            if not os.path.exists(path):
                os.makedirs(path)
            with open(os.path.join(path, files.getName()), 'w+') as f:
                for chunk in content.chunks():
                    f.write(chunk)
        else:
            path = os.path.join(path, 'content', str(
                contentid), files.getType() + 's')
            content = files.getFile()
            if not os.path.exists(path):
                os.makedirs(path)
            with open(os.path.join(path, files.getName()), 'w+') as f:
                for chunk in content.chunks():
                    f.write(chunk)

    ##
    # Recursive function for removing directories.
    ##
    def deleteFileTree(self, pdir):
        if not os.path.isdir(pdir):
            return False

        files = list(set(os.listdir(pdir)).difference([".", ".."]))

        for f in files:
            filepath = os.path.join(pdir, f)
            self.deleteFileTree(filepath) if os.path.isdir(
                filepath) else os.remove(filepath)

        return os.rmdir(pdir)

    ##
    # Read file content of given file and then return it
    ##
    def getContent(self, path):
        content = open(self.path + path)
        result = content.read()
        return result
