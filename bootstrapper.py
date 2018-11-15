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

import configparser
from os import putenv, system
from queue import Queue
from src.ScriptExecutor import ScriptExecutorPy, ScriptExecutorCxx


print("""
--------------------------------------------------------------------------------
                __
               / _)  Pipeline Boostrapper
        .-^^^-/ /
    __/       /
   <__.|_|-|_|

""")

config = configparser.ConfigParser()
config.read('conf.ini')
sections = config.sections()
sections.remove('GENERAL')
print("Scripts:\n{}".format(sections))

print("""
--------------------------------------------------------------------------------
""")


################################################################################
# Executors
#
executors = {}

communicationQueue = Queue()

for sectionName in sections:

    if config[sectionName]['language'] == 'c++':
        executors[config[sectionName]['name']] = ScriptExecutorCxx(config, sectionName, communicationQueue)

    elif config[sectionName]['language'] == 'python':
        executors[config[sectionName]['name']] = ScriptExecutorPy(config, sectionName, communicationQueue)

    else:
        print("Language not supported")
        exit()

input("\n --------> Press any key to start!")


handles = {}
for executorName, executorObj in executors.items():
    handles[executorName] = executorObj.START_WORK()

print("\nWaiting for any errors..")

threadName = communicationQueue.get()
print("Error occurs from {}..".format(threadName))

for executorName, executorObj in executors.items():
    if executorName != threadName:
        executorObj.stopNotification()

for executorName, executorObj in executors.items():
    #print("Waiting the for {}..".format(executorName))
    handles[executorName].join()

print("All threads are stopped..\nbye")
