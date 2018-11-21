# ==========================================================================
#
# Copyright (C) 2018 INAF - OAS Bologna
# Author: Leonardo Baroncelli <leonardo.baroncelli26@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ==========================================================================

#!/usr/bin/env python

from os import listdir, remove, stat, walk, errno
from os.path import join, splitext, basename
from enum import Enum     # for enum34, or the stdlib version
from operator import attrgetter



class File():
    def __init__(self, filename):
        self.filefullpath = filename
        self.filename = basename(self.filefullpath)
        self.filepath = self.filefullpath.replace(self.filename, '')

        if '.' in self.filename:
            self.fileext = self.filename.split(".")[-1]
        else:
            self.fileext = None


        self.file_st_mttime = stat(self.filefullpath).st_mtime
        self.consumed = False

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.filefullpath == other.filefullpath and self.file_st_mttime == other.file_st_mttime
        return False

    def __ne__(self, other):
        """Override the default Unequal behavior"""
        return self.filefullpath != other.filefullpath or self.file_st_mttime != other.file_st_mttime

    def __str__(self):
        return "\n"+self.filepath+self.filename+" "+str(self.file_st_mttime)+" "+str(self.consumed)

class ConsumeStrategy(Enum):
    KEEP = 1
    DELETE = 2


class FilesTracker():

    def __init__(self, directory, consumeStrategy = ConsumeStrategy.KEEP):

        self.directory = directory
        self.availableFiles = []
        self.removedFiles = []
        self.consumeStrategy = consumeStrategy


    def poll(self):
        polled = []
        for dirname, dirnames, filenames in walk(self.directory):
            for filename in filenames:
                polled.append(File(join(dirname, filename)))

        self.trackFiles(polled)



    # put a file in the tracked set if the file is not into consumed set and not into tracked set
    def trackFiles(self, files):

        # Check for deletions
        deteledFiles = []
        for f in self.availableFiles:
            if f not in files:
                self.removedFiles.append(f)
                self.availableFiles.remove(f)

        # Check for additions
        for f in files:
            if f not in self.availableFiles:
                self.availableFiles.append(f)

        #self.printSets()



    def getOldestFile(self, fileList = None):
        if fileList:
            return min(fileList,key=attrgetter('file_st_mttime'))
        else:
            return min(self.availableFiles,key=attrgetter('file_st_mttime'))


    def getFileFromFilename(self, filename, searchAlsoInRemovedList = False):
        file = None
        for f in self.availableFiles:
            if f.filename == filename:
                file = f
        if searchAlsoInRemovedList:
            for f in self.removedFiles:
                if f.filename == filename:
                    file = f

        return file

    def searchFile(self, extension, pattern='', excludePattern=''):

        goodFiles = []

        notConsumedFiles = [f for f in self.availableFiles if f.consumed==False]

        for f in notConsumedFiles:

            filename = f.filename
            file_extension = f.fileext

            good = False

            if file_extension == extension:

                if not bool(pattern) and not bool(excludePattern):
                    good = True

                if bool(pattern) and pattern in filename and not bool(excludePattern):
                    good = True

                if bool(excludePattern) and excludePattern not in filename and not bool(pattern):
                    good = True

                if bool(pattern) and bool(excludePattern) and pattern in filename and excludePattern not in filename:
                    good = True

                if good:
                    goodFiles.append(f)

        return goodFiles

    def printFiles(self):
        for f in self.availableFiles:
            print(f)


    def consume(self, file):

        toConsume = None
        fileToConsume = File(file)
        for f in self.availableFiles:
            if fileToConsume == f:
                toConsume = f

        toConsume.consumed = True

        if self.consumeStrategy == ConsumeStrategy.DELETE:
            self.removedFiles.append(toConsume)
            self.availableFiles.remove(toConsume)
            FilesTracker.silentremove(file)





    def printSets(self):
        print("\nTracked: ", self.availableFiles)
        print("Removed: ", self.removedFiles)

    def getFilenames(self):
        filenames = []
        for f in self.availableFiles:
            filenames.append(f)
        return filenames

    @staticmethod
    def silentremove(file):
        try:
            remove(file.filefullpath)
        except OSError as e: # this would be "except OSError, e:" before Python 2.6
            if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                raise # re-raise exception if a different error occurred
