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
from ExecutorUtils import ExecutorUtils as EU

class ExecutorUtilsTest(unittest.TestCase):

    def test_search_file_1(self):    # searchFile(fileNames, extension, pattern='', excludePattern='')

        files = ['a_pippo_b.txt', 'a_pippo_b.jpg', 'a_pluto_b.jpg', 'a_paperino_b.gif', 'a_paperino_pluto_b.gif', 'a_paperone_c.gif']

        found = EU.searchFile(files, '.txt')
        self.assertEqual(1, len(found))
        self.assertEqual('a_pippo_b.txt', found[0])

        found = EU.searchFile(files, '.jpg')
        self.assertEqual(2, len(found))
        self.assertEqual('a_pippo_b.jpg', found[0])
        self.assertEqual('a_pluto_b.jpg', found[1])

        found = EU.searchFile(files, '.jpg', pattern='pluto')
        self.assertEqual(1, len(found))
        self.assertEqual('a_pluto_b.jpg', found[0])

        found = EU.searchFile(files, '.jpg', excludePattern='pluto')
        self.assertEqual(1, len(found))
        self.assertEqual('a_pippo_b.jpg', found[0])

        found = EU.searchFile(files, '.gif', pattern='paperino', excludePattern='pluto')
        self.assertEqual(1, len(found))
        self.assertEqual('a_paperino_b.gif', found[0])







if __name__ == '__main__':

    unittest.main()
