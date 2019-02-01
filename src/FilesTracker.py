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
import re


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



    def searchFile(self, extension, pattern='', excludePattern='', relatedFilename='', relatedStategy=''):


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

                if good and FilesTracker.isRelatedTo(f, relatedFilename, relatedStategy):
                    goodFiles.append(f)

        return goodFiles

    @staticmethod
    def isRelatedTo(f, relatedFilepath, relatedStategy):
        if bool(relatedFilepath):
            relatedFilename = basename(relatedFilepath)
            return FilesTracker.execute_strategy(f.filename, relatedFilename, relatedStategy)
        else:
            return True

    @staticmethod
    def execute_strategy(f, relatedFilename, relatedStategy):
        if relatedStategy not in ['astri_filenames_strategy']:
            print("[FilesTracker] Error!! The strategy {} is not available!!".format(relatedStategy))
            exit(1)
        elif relatedStategy == 'astri_filenames_strategy':
            return FilesTracker.astri_filenames_strategy(f, relatedFilename)

    @staticmethod
    def astri_filenames_strategy(f, relatedFilename):

        m1 = re.search('astri_000_41_001_00001_R_(.+?)_001_', f)
        m2 = re.search('astri_000_41_001_00001_R_(.+?)_001_', relatedFilename)
        found1 = None
        found2 = None

        if m1: found1 = m1.group(1)
        if m2: found2 = m2.group(1)

        if found1 == found2 and found1 and found2:
            return True
        else:
            return False

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
    def getBasenameAndFilename(filepath):
        filename = basename(filepath)
        filepath = filepath.replace(filename, '')
        return (filename, filepath)


    @staticmethod
    def silentremove(file):
        try:
            remove(file.filefullpath)
        except OSError as e: # this would be "except OSError, e:" before Python 2.6
            if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                raise # re-raise exception if a different error occurred
