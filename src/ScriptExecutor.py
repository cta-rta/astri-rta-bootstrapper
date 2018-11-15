import configparser
from abc import ABC, abstractmethod
from os.path import isdir
from os import listdir, remove, system
from os.path import join, exists
from time import sleep, gmtime, strftime
from threading import Thread, Semaphore
import subprocess
import logging

from .ExecutorUtils import ExecutorUtils as EU

screenlock = Semaphore(value=1)

class ScriptExecutorBase(ABC):

    @abstractmethod
    def executeScript(self):
        pass

    def __init__(self, config, iniSectionName, communicationQueue):

        # The string-ID of the executor
        self.executorName = config[iniSectionName]['name']

        # Directories..
        self.inputDir = config['GENERAL']['dataPath']+'/'+config[iniSectionName]['inputDir']
        self.tempOutputDir = config['GENERAL']['tempOutputDir']+'/'+config[iniSectionName]['outputDir']    # do NOT invert tempOutputDir and outputDir!
        self.outputDir = config['GENERAL']['dataPath']+'/'+config[iniSectionName]['outputDir']

        # Filenames
        self.outputExt = config[iniSectionName]['outputExtension']
        self.outputTempName = 'out.'+config[iniSectionName]['outputExtension']+'.tmp'
        self.executableName = config[iniSectionName]['exeName']

        # Actual files
        self.executable = config[iniSectionName]['exeDir']+'/'+config[iniSectionName]['exeName']
        self.parFile = config[iniSectionName]['parFileDir']+'/'+config[iniSectionName]['parFileName']
        self.parFileName = config[iniSectionName]['parFileName']

        # Debugging
        self.debug = config.getboolean('GENERAL','debug')

        # Polling sleep
        self.sleepSec = config[iniSectionName]['sleepSec']

        # Logging
        logFile = join(config['GENERAL']['logDir'], config[iniSectionName]['name']+'_'+config['GENERAL']['logFilenameSuffix'])
        self.logger = self.setupLogger(config[iniSectionName]['name'], logFile)


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

            # Polling phase
            while not self.inputFilesFound and self.canContinue:

                self.searchForInputFiles()

                self.inputFilesFound = EU.isDictionaryAllSet(self.inputFiles)


            if not self.canContinue:
                break



            # Script phase
            toPrint = "[{} {}] All input files found. Script phase starts..".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()))
            self.LOG(toPrint)

            if not self.systemCall('cp '+self.parFile+' ./'): # Copy par file  -> create a function that move the par file and then check if the file is present
                break

            if not self.systemCall('mkdir -p '+self.tempOutputDir): # Create temp folder for temporary output
                break

            if not self.executeScript(): # The output files are written in a temp directory
                break


            # Clean phase
            if not self.systemCall('rm '+self.parFileName):
                break

            EU.cleanDirectory(self.inputDir)
            EU.cleanDictionary(self.inputFiles)
            self.inputFilesFound = False


        toPrint = "[{} {}] Quitting..".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        self.LOG(toPrint, printOnConsole = True)



    ###########################################################################
    # Utility functions
    #
    # return (bool err,string command, string strout,string stderr)
    def systemCall(self, command, logOutputOnFile = False):
        completedProcess = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if logOutputOnFile:
            toPrint = "\n\n\n[{} {}]\n{}".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()),completedProcess.stdout.decode("utf-8"))
            self.LOG(toPrint)

        if completedProcess.returncode == 1:
            return self.checkSystemCallOutput({ 'failed': True, 'script': completedProcess.args, 'stdout': completedProcess.stdout, 'stderr': completedProcess.stderr})
        else:
            return self.checkSystemCallOutput({ 'failed': False, 'script': completedProcess.args, 'stdout': completedProcess.stdout, 'stderr': completedProcess.stderr})


    def checkSystemCallOutput(self, systemCallOutput):
        if systemCallOutput['failed']:
            toPrint = "[{} {}]\nThe system call: {} has failed with error code 1.\nError: {}".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()), systemCallOutput['script'], systemCallOutput['stderr'].decode("utf-8"))
            self.LOG( EU.getErrorString(toPrint), printOnConsole = True)
            self.endJob()
            return False
        else:
            self.LOG("[{} {}] System call executed: {}".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()), systemCallOutput['script']))
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

        toPrint = "[{} {}] {}".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()),self.inputFiles)
        self.LOG(toPrint, printOnConsole = True)



    def setupLogger(self, name, log_file, level=logging.INFO):
        handler = logging.FileHandler(log_file)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

    def checkFilesAndDirectories(self):
        if not isdir(self.inputDir):
            toPrint = "\n[{}] ERROR!! the inputDir directory {} does not exist".format(self.executorName, self.inputDir)
            self.LOG(toPrint, printOnConsole = True)
            return False
        if not isdir(self.outputDir):
            toPrint = "\n[{}] ERROR!! the outputDir directory {} does not exist".format(self.executorName, self.outputDir)
            self.LOG(toPrint, printOnConsole = True)
            return False
        if not exists(self.executable):
            toPrint = "\n[{}] ERROR!! the executable {} does not exist".format(self.executorName, self.executable)
            self.LOG(toPrint, printOnConsole = True)
            return False
        if not exists(self.parFile):
            toPrint = "\n[{}] ERROR!! the parFile {} does not exist".format(self.executorName, self.parFile)
            self.LOG(toPrint, printOnConsole = True)
            return False
        return True

    def endJob(self):
        self.canContinue = False
        self.commQueue.put(self.executorName)

    def stopNotification(self):
        self.canContinue = False
        self.LOG("[{} {}] Got stop notification from main.".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime())))

    def printInfo(self):
        toPrint = "\nMy name is: {} \nI watch the dir: {}\nI look for: {}\nI run: {}".format(self.executorName,self.inputDir,self.searchForExtsList,self.executable)
        self.LOG(toPrint, printOnConsole = True)

    def LOG(self, string, printOnConsole = False):
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

        command = self.executable+' '+self.inputFiles['lv2a']+' '+self.tempOutputDir+'/'+self.outputTempName

        toPrint = "[{} {}] ---> SCRIPT {} IS RUNNING... PATIENCE.. <--".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()), self.executableName)
        self.LOG(toPrint, printOnConsole = True)

        res = self.systemCall(command, logOutputOnFile = True)

        if not res:
            return False


        moveCommand = 'cp '+self.tempOutputDir+'/'+self.outputTempName+' '+self.outputDir

        if not self.systemCall(moveCommand): # the files are moved into the output directory
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
