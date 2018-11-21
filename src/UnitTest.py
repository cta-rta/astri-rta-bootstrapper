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

from FilesTracker import FilesTracker
from FilesTracker import ConsumeStrategy
from FilesTracker import File


class FilesTrackerTest(unittest.TestCase):

    files = []


    def setUp(self):

        system('mkdir -p test_dir/files_dir')

        self.files = ['test_dir/files_dir/a.hpp',
                      'test_dir/files_dir/b.hpp',
                      'test_dir/files_dir/c.png',
                      'test_dir/files_dir/d.png',
                      'test_dir/files_dir/e.jpg',
                      'test_dir/files_dir/f.jpg',
                      'test_dir/files_dir/g.gif',
                      'test_dir/files_dir/h.gif',
                      'test_dir/files_dir/e.txt',
                      'test_dir/files_dir/f_xyz.txt',
                      'test_dir/files_dir/f_xyz_qwerty.txt',
                      'test_dir/files_dir/f_qwerty.txt'
                     ]

        for file in self.files:
            system('touch '+file)

    def test_file_class(self):
        f = File(self.files[0])
        self.assertEqual('test_dir/files_dir/a.hpp', f.filefullpath)
        self.assertEqual('test_dir/files_dir/', f.filepath)
        self.assertEqual('a.hpp', f.filename)
        self.assertEqual('hpp', f.fileext)
        self.assertEqual(False, f.consumed)


    def test_poll(self):
        ft = FilesTracker('test_dir/files_dir')
        ft.poll()

        self.assertEqual(len(self.files), len(ft.availableFiles))
        #self.assertEqual(True,f in ft.availableFiles)

    def test_oldestFile(self):
        system('mkdir -p test_dir/files_dir_2')
        system('touch test_dir/files_dir_2/a.txt')
        system('touch test_dir/files_dir_2/b.txt')
        system('touch test_dir/files_dir_2/c.txt')

        ft = FilesTracker('test_dir/files_dir_2')
        ft.poll()

        oldestFile = ft.getOldestFile()
        self.assertEqual('test_dir/files_dir_2/a.txt', oldestFile.filefullpath)

        system('rm test_dir/files_dir_2/a.txt')
        ft.poll()

        oldestFile = ft.getOldestFile()
        self.assertEqual('test_dir/files_dir_2/b.txt', oldestFile.filefullpath)

        system('rm -r test_dir/files_dir_2')

    def test_consume_keep_strategy_and_poll(self):
        f = File('test_dir/files_dir/a.hpp')

        ft = FilesTracker('test_dir/files_dir')
        ft.poll()
        ft.consume(f)

        file = ft.getFileFromFilename('a.hpp')
        self.assertEqual(True, file.consumed) # the file is consumed but not removed

    def test_consume_delete_strategy_and_poll(self):
        f = File('test_dir/files_dir/a.hpp')

        ft = FilesTracker('test_dir/files_dir', consumeStrategy = ConsumeStrategy.DELETE)
        ft.poll()
        ft.consume(f)

        file = ft.getFileFromFilename('a.hpp')
        self.assertEqual(None, file) # the file is consumed and removed

        file = ft.getFileFromFilename('a.hpp', searchAlsoInRemovedList=True)
        self.assertEqual(True, file.consumed) # the file is consumed and removed


    def test_search_file(self):    # searchFile(fileNames, extension, pattern='', excludePattern='')

        ft = FilesTracker('test_dir/files_dir')
        ft.poll()
        filesTxtFound = ft.searchFile('txt')
        filesHppFound = ft.searchFile('hpp')
        filesJpgFound = ft.searchFile('jpg')
        filesPngFound = ft.searchFile('png')
        filesGifFound = ft.searchFile('gif')
        self.assertEqual(4, len(filesTxtFound))
        self.assertEqual(2, len(filesHppFound))
        self.assertEqual(2, len(filesJpgFound))
        self.assertEqual(2, len(filesPngFound))
        self.assertEqual(2, len(filesGifFound))

        f1 = File('test_dir/files_dir/f_xyz.txt')
        f2 = File('test_dir/files_dir/f_xyz_qwerty.txt')
        filesFounds = ft.searchFile('txt', pattern='xyz')
        self.assertEqual(2, len(filesFounds))
        self.assertEqual(True, f1 in filesFounds and f2 in filesFounds)

        f1 = File('test_dir/files_dir/e.txt')
        f2 = File('test_dir/files_dir/f_qwerty.txt')
        filesFounds = ft.searchFile('txt', excludePattern='xyz')
        self.assertEqual(2, len(filesFounds))
        self.assertEqual(True, f1 in filesFounds and f2 in filesFounds)

        f = File('test_dir/files_dir/f_qwerty.txt')
        filesFounds = ft.searchFile('txt', pattern='qwerty', excludePattern='xyz')
        self.assertEqual(1, len(filesFounds))
        self.assertEqual(True, f in filesFounds)



    def tearDown(self):
        system('rm -r test_dir')




if __name__ == '__main__':
    unittest.main()
