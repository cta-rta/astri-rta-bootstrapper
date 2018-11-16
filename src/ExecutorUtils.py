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

from os import listdir, remove, stat
from os.path import join, splitext

class ExecutorUtils():
 

    @staticmethod
    def deleteFilesInDirectory(fileList, dir):
        for f in fileList:
            try:
                remove(join(dir, f))
            except FileNotFoundError:
                pass

    @staticmethod
    def isDictionaryAllSet(dict):
        for key, val in dict.items():
            if val is None:
                return False
        return True

    @staticmethod
    def searchFile(fileNames, extension, pattern='', excludePattern=''):
        goodFiles = []
        for f in fileNames:

            filename, file_extension = splitext(f)

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


    @staticmethod
    def getOlderFile(fileNames, filesDir):
        if len(fileNames) == 1:
            return fileNames[0]

        rank = {}
        for f in fileNames:
            #print("f:", f)
            f_fullpath = join(filesDir,f)
            #print("f_fullpath: ", f_fullpath)
            rank[f]=stat(f_fullpath).st_mtime
        #print(rank)

        timestampMin = rank[fileNames[0]]
        filenameMin = fileNames[0]
        for filename, timestamp in rank.items():
            if timestamp < timestampMin:
                timestampMin = timestamp
                filenameMin = filename
        #print("filenameMin, ts: ", filenameMin, timestampMin)
        return filenameMin




    @staticmethod
    def getErrorString(string):
        return '\n** ERROR! **************************************************\n'+string+'\n************************************************************\n\n'
