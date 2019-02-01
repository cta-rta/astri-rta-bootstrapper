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
from os.path import join, exists, splitext
from time import sleep, gmtime, strftime, time
from threading import Thread
import subprocess
import logging
from ast import literal_eval

from .ExecutorUtils import ExecutorUtils as EU
from .FilesTracker import FilesTracker, ConsumeStrategy

class ScriptExecutorBase(ABC):

    @abstractmethod
    def executeScript(self):
        pass

    def __init__(self, config, iniSectionName, communicationQueue):

        # The string-ID of the executor
        self.executorName = config[iniSectionName]['name']
        self.interpreter = config[iniSectionName]['interpreter']

        # Directories
        self.inputDir      = config[iniSectionName]['inputDir']

        # Files tracker
        if config.getboolean('GENERAL','keepInputFiles'):
            self.ft = FilesTracker(self.inputDir, consumeStrategy=ConsumeStrategy.KEEP)
        else:
            self.ft = FilesTracker(self.inputDir, consumeStrategy=ConsumeStrategy.DELETE)


        # Filenames
        self.executableName = config[iniSectionName]['exeName']

        # Existing files
        self.executable  = join(config[iniSectionName]['exeDir'],config[iniSectionName]['exeName'])
        self.parFile     = join(config[iniSectionName]['parFileDir'],config[iniSectionName]['parFileName'])
        self.parFileName = config[iniSectionName]['parFileName']

        # Par file management
        self.updateParValuesWith = literal_eval(config[iniSectionName]['updateParValuesWith'])

        # Debugging
        self.debug = config.getboolean('GENERAL','debug')

        # Polling sleep
        self.sleepSec = config[iniSectionName]['sleepSec']

        # Logging
        logFile = join('logs', config[iniSectionName]['name']+'_'+strftime("%Y-%m-%d_%H:%M:%S", gmtime())+'_log.txt')
        self.logger = self.setupLogger(config[iniSectionName]['name'], logFile)

        # Env
        try:
            self.envVarsDict = literal_eval(config[iniSectionName]['envVars'])
        except ValueError as ve:
            self.LOG("ERROR {}!\nCheck [envVars] configuration file option.".format(ve), printOnConsole = True, addErrorDecorator = True)
            exit()

        # Script input file management
        self.scriptInputsDict = literal_eval(config[iniSectionName]['scriptInputsDict'])


        self.inputArgs = {} # Those are the files searched by the executor to run the script. Dictionary -> { number : filepath, ..  }

        for key,values in self.scriptInputsDict.items():

            if values['type'] == 'output':
                self.inputArgs[key] = 'tmp/'+key+'_'+values['output_exe']+'_tmp'

            elif values['type'] == 'inputfile':
                self.inputArgs[key] = None

            else:
                print("Error!! Value {} for 'type' parameter is not supported! Supported values=inputfile, output".format(values['type']))
                exit()

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

                sleep(int(self.sleepSec))

                self.ft.poll()

                self.searchForInputFiles()

                self.inputFilesFound = EU.isDictionaryAllSet(self.inputArgs)


            if not self.canContinue:
                break



            ####################
            # Script run phase #
            ####################
            if not self.systemCall('cp '+self.parFile+' ./'): # Copy par file into the current dir
                break

            if not self.systemCall('mkdir -p tmp'): # Create temp folder for temporary output
                break


            self.LOG("---> SCRIPT {} IS RUNNING... PATIENCE.. <--".format(self.executableName), printOnConsole = True)

            if not self.executeScript(): # The output files are written in a temp directory
                break

            if not self.moveOutputFiles(): # Moving all temporary output files
                break

            #if not self.systemCall('rm -rf tmp/*'): # Destroy the temp folder for temporary output
            #    break

            if not self.systemCall('rm '+self.parFileName): # Remove the par
                break


            for input_number, input_path in self.inputArgs.items():

                if self.scriptInputsDict[input_number]['type'] == 'inputfile' and self.scriptInputsDict[input_number]['useforever'] == 'no':

                    self.ft.consume(self.inputArgs[input_number])          # Mark the file as 'consumed'

                    self.inputArgs[input_number] = None                    # Clean the input files dictionary

                if not self.inputArgs[input_number]:
                    self.inputFilesFound = False                                   # Clean bool var


        self.LOG("Quitting..", printOnConsole = True)



    ###########################################################################
    # Utility functions
    #
    # return (bool err,string command, string strout,string stderr)
    def systemCall(self, command, logOutputOnFile = False, envVars = None, shell=True):

        print("Running: ", command)
        completedProcess = subprocess.run(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=envVars)

        if logOutputOnFile and completedProcess.stdout:
            self.LOG("{}".format(completedProcess.stdout.decode("utf-8")))

        if logOutputOnFile and completedProcess.stderr:
            self.LOG("{}".format(completedProcess.stderr.decode("utf-8")))

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

        # scriptInputsDict = {
        #           '1':{'type':'inputfile', 'ext':'lv2b', 'pattern':'', 'exludepattern':'irf', 'value':'', 'useforever':'no', 'relatedTo' : ''},
        #           '2':{'type':'inputfile', 'ext':'lv2b', 'pattern':'irf', 'exludepattern':'', 'value':'', 'useforever':'yes', 'relatedTo' : ''},
        #           '3':{'type':'inputfile', 'ext':'lv0',  'pattern':'', 'exludepattern':'', 'value':'', 'useforever':'no', 'relatedTo' : '1'},
        # }

        for input_number, input_path in self.inputArgs.items():

            # if input type is 'file'
            if self.scriptInputsDict[input_number]['type'] == 'inputfile':

                # if file is not found yet
                if input_path is None:

                    newFiles = []

                    relatedFilename = ''
                    relatedToIndex = self.scriptInputsDict[input_number]['relatedTo']
                    relatedStategy = self.scriptInputsDict[input_number]['relatedStategy']
                    canSearchRelated = False
                    if bool(relatedToIndex) and bool(self.inputArgs[relatedToIndex]):
                        relatedFilename = self.inputArgs[relatedToIndex]
                        canSearchRelated = True

                    if not bool(relatedToIndex) or canSearchRelated:
                        newFiles = self.ft.searchFile(self.scriptInputsDict[input_number]['ext'], pattern = self.scriptInputsDict[input_number]['pattern'], excludePattern = self.scriptInputsDict[input_number]['exludepattern'], relatedFilename = relatedFilename, relatedStategy = relatedStategy)

                    # take the oldest file
                    if len(newFiles) >= 1:
                        oldestFile = self.ft.getOldestFile(newFiles)
                        self.inputArgs[input_number] = oldestFile.filefullpath

        self.LOG("\n{\n" + "\n".join("{}: {}".format(k, v) for k, v in self.inputArgs.items()) + "\n}", printOnConsole = True)



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
        if not exists(self.executable):
            toPrint = "\nERROR!! the executable {} does not exist".format(self.executable)
            self.LOG(toPrint, printOnConsole = True, addErrorDecorator = True)
            return False
        if not exists(self.parFile):
            toPrint = "\nERROR!! the parFile {} does not exist".format(self.parFile)
            self.LOG(toPrint, printOnConsole = True, addErrorDecorator = True)
            return False
        for key,values in self.scriptInputsDict.items():
            if values['type'] == 'output':
                if not isdir(values['output_dir']):
                    toPrint = "\nERROR!! the outputDir directory {} does not exist".format(values['output_dir'])
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
        toPrint = "\nMy name is: "+str(self.executorName)+ "\
                   \nI watch the dir: "+str(self.inputDir)+ "\
                   \nI look for: \n{\n" + "\n".join("{}: {}".format(k, v) for k, v in self.scriptInputsDict.items()) + "\n} \
                   \nI run: "+str(self.executable)+ "\
                   \nI use: \n{\n" + "\n".join("{}: {}".format(k, v) for k, v in self.envVarsDict.items()) + "\n} \
                   \n Input args: \n{\n" + "\n".join("{}: {}".format(k, v) for k, v in self.inputArgs.items()) + "\n} "

        self.LOG(toPrint, printOnConsole = True)

    def LOG(self, string, printOnConsole = False, addErrorDecorator = False):

        string = "\n[{} {}] ".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()))+string

        if addErrorDecorator:
            string = EU.getErrorString(string)

        if printOnConsole or self.debug:
            print(string)
        self.logger.info(string)

    def moveOutputFiles(self):
        noErrors = True
        for key,values in self.scriptInputsDict.items():

            if values['type'] == 'output':

                filepath = values['output_dir']
                filename = ''
                if values['filenameRelatedTo'] == 'null':
                    filename = values['filename']+'.'+values['output_exe']
                else:
                    relatedToIndex = values['filenameRelatedTo']
                    father_filename, father_filepath = FilesTracker.getBasenameAndFilename(self.inputArgs[relatedToIndex])
                    filename = splitext(father_filename)[0]
                    filename = filename+'.'+values['output_exe']


                noErrors = self.systemCall('mv '+self.inputArgs[key]+' '+join(filepath, filename))
                if not noErrors:
                    break

        return noErrors

    # Follia:
    # - Per ogni riga del par file
    #    - per ogni campo da modificare
    #       - se il campo è nella riga
    #          - si prende il numero corrispondente all'input
    #          - si prende il path+nome del file corrispondente al numero
    #          - si modifica la riga
    def updateParFile(self):
        updated_config = ""
        with open('./'+self.parFileName) as af:
            lines = af.readlines()
            #print("Original: ",lines)
            for l in lines:
                #print("l: ",l)
                replaced = False
                firstValueInLine = self.extractFirstValueFromParLine(l)
                #print("firstValueInLine: ", firstValueInLine)

                for pField in self.updateParValuesWith.keys():
                    #print("Searching ",pField," in ", firstValueInLine)
                    if pField == firstValueInLine:
                        #print("Found: ",pField)
                        inputNumber = self.updateParValuesWith[pField]
                        #print("pValueExt: ",pValueExt)
                        pValue = self.inputArgs[inputNumber]
                        #print("pValue: ",pValue)
                        updated_config += pField+',  s, h, "'+pValue+'" , , , "abcde"\n'
                        #print("updated_config: ",updated_config)
                        replaced = True
                    #else:
                        #print("Not found ",pField)
                if not replaced:
                    updated_config += l
                    #print("updated_config: ",updated_config)
        #print("Aggiornato: \n",updated_config)
        with open('./'+self.parFileName, "w") as ac:
            ac.write(updated_config)


    def extractFirstValueFromParLine(self, line):
        if ',' in line:
            #print("LINE: ", line)
            values = line.split(",")
            return values[0]
        return line





################################################################################
#
#
class ScriptExecutorCxx(ScriptExecutorBase):

    def __init__(self, config, iniSectionName, communicationQueue):
        super().__init__(config, iniSectionName, communicationQueue)

    def executeScript(self):

        command = self.executable+' '

        if not bool(self.updateParValuesWith):

            for inputArg in self.inputArgs.values():
                command += inputArg+' '

        else:
            self.updateParFile()

        self.LOG(command, printOnConsole=True)

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

        command = [self.interpreter, self.executable]

        if not bool(self.updateParValuesWith):

            for inputArg in self.inputArgs:
                command.append(inputArg)

        else:
            self.updateParFile()

        self.LOG(''.join(command), printOnConsole=True)

        if not self.systemCall('python --version', logOutputOnFile = True):
            return False
        if not self.systemCall('which python', logOutputOnFile = True):
            return False
        if not self.systemCall(["python", "--version"], logOutputOnFile = True, shell=False):
            return False
        if not self.systemCall(["which", "python"], logOutputOnFile = True, shell=False):
            return False

        if not self.systemCall(command, logOutputOnFile = True, envVars=self.envVarsDict, shell=False):
            return False

        return True
