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

from os import listdir, remove, stat, walk
from os.path import join, splitext


class FilesTracker():

    """
        TRACKED_FILE ----> CONSUMED_FILE
    """

    def __init__(self, directory):

        self.directory = directory
        self.trackedFiles = set()
        self.consumedFiles = set()

    """
        The poll will read the directory and will update the FileTracker data structures.
    """
    def poll(self):

        polled = set()

        for dirname, dirnames, filenames in walk(self.directory):

            for filename in filenames:
                polled.add(join(dirname, filename))


        self.trackedFiles = self.trackFiles(polled, self.trackedFiles, self.consumedFiles)


    def consumed(self, file):
        self.trackedFiles.remove(file)
        self.consumedFiles.add(file)


    # put a file in the tracked set if the file is not into consumed set and not into tracked set
    @staticmethod
    def trackFiles(files, trackedFiles, consumedFiles):

        newFiles = files.difference((trackedFiles.union(consumedFiles)))

        for f in newFiles:
            trackedFiles.add(f)

        return trackedFiles


    def searchFile(self, extension, pattern='', excludePattern=''):

        goodFiles = set()

        for f in self.trackedFiles:

            filename, file_extension = splitext(f)
            #print("\nfilename: ", filename)
            #print("file_extension: ", file_extension)

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
                    goodFiles.add(f)

        return goodFiles
