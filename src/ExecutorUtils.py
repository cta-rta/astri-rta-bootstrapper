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

from os import listdir, remove
from os.path import join, splitext

class ExecutorUtils():

    @staticmethod
    def isDictionaryAllSet(dict):
        for key, val in dict.items():
            if val is None:
                return False
        return True


    @staticmethod
    def getErrorString(string):
        return '\n** ERROR! **************************************************\n'+string+'\n************************************************************\n\n'
