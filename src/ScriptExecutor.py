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
from abc import ABC, abstractmethod
from os.path import isdir
from os import listdir, system
from os.path import join, exists
from time import sleep, gmtime, strftime
from threading import Thread
import subprocess
import logging
from ast import literal_eval

from .ExecutorUtils import ExecutorUtils as EU


class ScriptExecutorBase(ABC):

    @abstractmethod
    def executeScript(self):
        pass

    def __init__(self, config, iniSectionName, communicationQueue):

        # The string-ID of the executor
        self.executorName = config[iniSectionName]['name']

        # Directories
        self.inputDir = config['GENERAL']['dataPath']+'/'+config[iniSectionName]['inputDir']
        self.tempOutputDir = config['GENERAL']['tempOutputDir']+'/'+config[iniSectionName]['outputDir']    # do NOT invert tempOutputDir and outputDir!
        self.outputDir = config['GENERAL']['dataPath']+'/'+config[iniSectionName]['outputDir']

        # Filenames
        self.outputTempName = config[iniSectionName]['outputFilename']+'.tmp'
        self.outputFilename = config[iniSectionName]['outputFilename']
        self.executableName = config[iniSectionName]['exeName']

        # Existing files
        self.executable = config[iniSectionName]['exeDir']+'/'+config[iniSectionName]['exeName']
        self.parFile = config[iniSectionName]['parFileDir']+'/'+config[iniSectionName]['parFileName']
        self.parFileName = config[iniSectionName]['parFileName']

        # Debugging
        self.debug = config.getboolean('GENERAL','debug')

        # Polling sleep
        self.sleepSec = config[iniSectionName]['sleepSec']

        # Logging
        logFile = join(config['GENERAL']['logDir'], config[iniSectionName]['name']+'_'+strftime("%Y-%m-%d_%H:%M:%S", gmtime())+'_log.txt')
        self.logger = self.setupLogger(config[iniSectionName]['name'], logFile)

        # Env
        try:
            self.envVarsDict = literal_eval(config[iniSectionName]['envVars'])
        except ValueError as ve:
            self.LOG("ERROR {}!\nCheck [envVars] configuration file option.".format(ve), printOnConsole = True, addErrorDecorator = True)
            exit()

        # Script input file management
        self.searchForExtsList = EU.splitToList(config[iniSectionName]['inputExtensions'])
        self.inputFiles = {} # Those are the files searched by the executor to run the script. Dictionary -> { extension: filepath, ..  }
        for ext in self.searchForExtsList:
            self.inputFiles[ext] = None
        self.inputFilesFound = False


        # Communication queue in order to stop the executors
        self.commQueue = communicationQueue
        self.canContinue = True

        # Starting output
        self.printInfo()


    def threaded(fn):
        def wrapper(*args, **kwargs):
            thread = Thread(target=fn, args=args, kwargs=kwargs)
            thread.start()
            return thread
        return wrapper

    ################################################################################
    # Core function
    #
    @threaded
    def START_WORK(self):

        # check
        if not self.checkFilesAndDirectories():
            self.endJob()

        while self.canContinue:

            #################
            # Polling phase #
            #################
            while not self.inputFilesFound and self.canContinue:

                self.searchForInputFiles()

                self.inputFilesFound = EU.isDictionaryAllSet(self.inputFiles)


            if not self.canContinue:
                break



            ####################
            # Script run phase #
            ####################
            if not self.systemCall('cp '+self.parFile+' ./'): # Copy par file into the current dir
                break

            if not self.systemCall('mkdir -p '+self.tempOutputDir): # Create temp folder for temporary output
                break

            if not self.executeScript(): # The output files are written in a temp directory
                break

            if not self.systemCall('mv '+join(self.tempOutputDir,self.outputTempName)+' '+join(self.outputDir, self.outputFilename)): # Move output file when the script finished
                return False

            if not self.systemCall('rm '+self.parFileName): # Remove the par
                break

            EU.cleanDirectory(self.inputDir) # Remove the input files
            EU.cleanDictionary(self.inputFiles) # Clean the input files dictionary
            self.inputFilesFound = False


        self.LOG("Quitting..", printOnConsole = True)



    ###########################################################################
    # Utility functions
    #
    # return (bool err,string command, string strout,string stderr)
    def systemCall(self, command, logOutputOnFile = False, envVars = None):

        completedProcess = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env = envVars)

        if logOutputOnFile:
            self.LOG("{}".format(completedProcess.stdout.decode("utf-8")))

        if completedProcess.returncode == 1:
            return self.checkSystemCallOutput({ 'failed': True, 'script': completedProcess.args, 'stdout': completedProcess.stdout, 'stderr': completedProcess.stderr})
        else:
            return self.checkSystemCallOutput({ 'failed': False, 'script': completedProcess.args, 'stdout': completedProcess.stdout, 'stderr': completedProcess.stderr})


    def checkSystemCallOutput(self, systemCallOutput):
        if systemCallOutput['failed']:
            toPrint = "\nThe system call: {} has failed with error code 1.\nError: {}".format(systemCallOutput['script'], systemCallOutput['stderr'].decode("utf-8"))
            self.LOG(toPrint, printOnConsole = True, addErrorDecorator = True)
            self.endJob()
            return False
        else:
            self.LOG("System call executed: {}".format(systemCallOutput['script']))
            return True


    # Polling
    def searchForInputFiles(self):

        sleep(int(self.sleepSec))
        currentFiles = listdir(self.inputDir)

        for ext, val in self.inputFiles.items():
            if val is None:
                newFile = EU.searchFileWithExtension(currentFiles, ext)
                if newFile:
                    self.inputFiles[ext] = join(self.inputDir, newFile)

        self.LOG("{}".format(self.inputFiles), printOnConsole = True)



    def setupLogger(self, name, log_file, level=logging.INFO):
        handler = logging.FileHandler(log_file)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

    def checkFilesAndDirectories(self):
        if not isdir(self.inputDir):
            toPrint = "\nERROR!! the inputDir directory {} does not exist".format(self.inputDir)
            self.LOG(toPrint, printOnConsole = True, addErrorDecorator = True)
            return False
        if not isdir(self.outputDir):
            toPrint = "\nERROR!! the outputDir directory {} does not exist".format(self.outputDir)
            self.LOG(toPrint, printOnConsole = True, addErrorDecorator = True)
            return False
        if not exists(self.executable):
            toPrint = "\nERROR!! the executable {} does not exist".format(self.executable)
            self.LOG(toPrint, printOnConsole = True, addErrorDecorator = True)
            return False
        if not exists(self.parFile):
            toPrint = "\nERROR!! the parFile {} does not exist".format(self.parFile)
            self.LOG(toPrint, printOnConsole = True, addErrorDecorator = True)
            return False
        return True

    def endJob(self):
        self.canContinue = False
        self.commQueue.put(self.executorName)

    def stopNotification(self):
        self.canContinue = False
        self.LOG("Got stop notification from main.")

    def printInfo(self):
        toPrint = "\nMy name is: {} \nI watch the dir: {}\nI look for: {}\nI run: {}\nI use {}".format(self.executorName,self.inputDir,self.searchForExtsList,self.executable, self.envVarsDict)
        self.LOG(toPrint, printOnConsole = True)

    def LOG(self, string, printOnConsole = False, addErrorDecorator = False):

        string = "\n[{} {}] ".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()))+string

        if addErrorDecorator:
            string = EU.getErrorString(string)

        if printOnConsole or self.debug:
            print(string)
        self.logger.info(string)

################################################################################
#
#
class ScriptExecutorCxx(ScriptExecutorBase):

    def __init__(self, config, iniSectionName, communicationQueue):
        super().__init__(config, iniSectionName, communicationQueue)

    def executeScript(self):

        self.LOG("---> SCRIPT {} IS RUNNING... PATIENCE.. <--".format(self.executableName), printOnConsole = True)

        command = self.executable+' '+self.inputFiles['lv2a']+' '+join(self.tempOutputDir,self.outputTempName)
        if not self.systemCall(command, logOutputOnFile = True, envVars=self.envVarsDict):
            return False

        return True





################################################################################
#
#
class ScriptExecutorPy(ScriptExecutorBase):

    def __init__(self, config, iniSectionName, communicationQueue):
        super().__init__(config, iniSectionName, communicationQueue)


    def executeScript(self):
        print("Py RUNNING SCRIPT!!!")
