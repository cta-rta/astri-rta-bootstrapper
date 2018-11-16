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

import unittest
from os import system

from ExecutorUtils import ExecutorUtils as EU
from FilesTracker import FilesTracker

class ExecutorUtilsTest(unittest.TestCase):

    def test_search_file_1(self):    # searchFile(fileNames, extension, pattern='', excludePattern='')

        files = ['a_pippo_b.txt', 'a_pippo_b.jpg', 'a_pluto_b.jpg', 'a_paperino_b.gif', 'a_paperino_pluto_b.gif', 'a_paperone_c.gif']

        filesFound = EU.searchFile(files, '.txt')
        self.assertEqual(1, len(filesFound))
        self.assertEqual('a_pippo_b.txt', filesFound[0])

        filesFound = EU.searchFile(files, '.jpg')
        self.assertEqual(2, len(filesFound))
        self.assertEqual('a_pippo_b.jpg', filesFound[0])
        self.assertEqual('a_pluto_b.jpg', filesFound[1])

        filesFound = EU.searchFile(files, '.jpg', pattern='pluto')
        self.assertEqual(1, len(filesFound))
        self.assertEqual('a_pluto_b.jpg', filesFound[0])

        filesFound = EU.searchFile(files, '.jpg', excludePattern='pluto')
        self.assertEqual(1, len(filesFound))
        self.assertEqual('a_pippo_b.jpg', filesFound[0])

        filesFound = EU.searchFile(files, '.gif', pattern='paperino', excludePattern='pluto')
        self.assertEqual(1, len(filesFound))
        self.assertEqual('a_paperino_b.gif', filesFound[0])


class FilesTrackerTest(unittest.TestCase):

    def setUp(self):

        system('mkdir -p test_dir/files_dir')

        files = ['file1.hpp',
                 'file2.hpp',
                 'file3.png',
                 'a_pippo_b.txt',
                 'a_pippo_b.jpg',
                 'a_pluto_b.jpg',
                 'a_paperino_b.gif',
                 'a_paperino_pluto_b.gif',
                 'a_paperone_c.gif']

        for file in files:
            system('touch test_dir/files_dir/'+file)



    def test_track_files(self):

        files         = {'a.txt', 'b.txt', 'c.png'}
        trackedFiles  = { 'c.png' }
        consumedFiles = { 'b.txt' }

        trackedFiles = FilesTracker.trackFiles(files, trackedFiles, consumedFiles)

        self.assertEqual(2, len(trackedFiles))
        self.assertEqual(True,'a.txt' in trackedFiles)
        self.assertEqual(True,'c.png' in trackedFiles)


    def test_poll(self):
        ft = FilesTracker('test_dir/files_dir')

        ft.poll()

        print(ft.trackedFiles)

        self.assertEqual(9, len(ft.trackedFiles))
        self.assertEqual(True,'test_dir/files_dir/file1.hpp' in ft.trackedFiles)
        self.assertEqual(True,'test_dir/files_dir/file2.hpp' in ft.trackedFiles)
        self.assertEqual(True,'test_dir/files_dir/file3.png' in ft.trackedFiles)


    def test_search_file_1(self):    # searchFile(fileNames, extension, pattern='', excludePattern='')


        ft = FilesTracker('test_dir/files_dir')

        ft.poll()

        filesFound = ft.searchFile('.txt')

        self.assertEqual(1, len(filesFound))
        self.assertEqual(True, 'test_dir/files_dir/a_pippo_b.txt' in filesFound)

        filesFound = ft.searchFile('.jpg')
        self.assertEqual(2, len(filesFound))
        self.assertEqual(True, 'test_dir/files_dir/a_pippo_b.jpg' in filesFound)
        self.assertEqual(True, 'test_dir/files_dir/a_pluto_b.jpg' in filesFound)

        filesFound = ft.searchFile('.jpg', pattern='pluto')
        self.assertEqual(1, len(filesFound))
        self.assertEqual(True, 'test_dir/files_dir/a_pluto_b.jpg' in filesFound)

        filesFound = ft.searchFile('.jpg', excludePattern='pluto')
        self.assertEqual(1, len(filesFound))
        self.assertEqual(True, 'test_dir/files_dir/a_pippo_b.jpg' in filesFound)

        filesFound = ft.searchFile('.gif', pattern='paperino', excludePattern='pluto')
        self.assertEqual(1, len(filesFound))
        self.assertEqual(True, 'test_dir/files_dir/a_paperino_b.gif' in filesFound)

    def tearDown(self):
        system('rm -r test_dir')




if __name__ == '__main__':

    unittest.main()
