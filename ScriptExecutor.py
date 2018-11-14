import configparser
from abc import ABC, abstractmethod
from os.path import isdir
from os import listdir, remove
from os.path import join
from time import sleep, gmtime, strftime
import threading
from threading import Semaphore

screenlock = Semaphore(value=1)

class ScriptExecutorBase(ABC):

    @abstractmethod
    def executeScript(self):
        pass

    def __init__(self, config, iniSectionName):

        self.executorName = config[iniSectionName]['name']
        self.inputDir = config['GENERAL']['dataPath']+'/'+config[iniSectionName]['inputDir']
        self.searchForExts = self.splitToList(config[iniSectionName]['inputsExt'])
        self.executable = config[iniSectionName]['exePath']+'/'+config[iniSectionName]['exeName']
        self.outputDir = config['GENERAL']['dataPath']+'/'+config[iniSectionName]['outputDir']
        self.sleepSec = config[iniSectionName]['sleepSec']
        self.canContinue = True
        self.inputFilesFound = False

        # Dictionary object -> { extension: filepath, ..  }
        self.inputFiles = {}
        for ext in self.searchForExts:
            self.inputFiles[ext] = None

        print("\nExecutor started!")
        self.printInfo()

        if not isdir(self.inputDir):
            print("\n[{}] ERROR!! the directory {} does not exist".format(self.executorName, self.inputDir))
            exit()


    def threaded(fn):
        def wrapper(*args, **kwargs):
            threading.Thread(target=fn, args=args, kwargs=kwargs).start()
        return wrapper

    ################################################################################
    # Core function
    #
    @threaded
    def START_WORK(self):
        while self.canContinue:

            # Polling phase
            while not self.inputFilesFound:
                self.searchForInputFiles()
                self.inputFilesFound = self.isInputComplete()

            # Running script phase
            self.executeScript()

            # Clean phase
            self.cleanInputDirectory()
            self.cleanDictionary()
            self.inputFilesFound = False








    ###########################################################################
    # Utility functions
    #
    def printInfo(self):
        print("Info: \nMy name is: {} \nI watch the dir: {}\nI look for: {}\nI run: {}".format(self.executorName,self.inputDir,self.searchForExts,self.executable))

    def searchForInputFiles(self):

        sleep(int(self.sleepSec))

        self.currentFiles = listdir (self.inputDir)

        screenlock.acquire()
        print("\n[{} {}] Polled directory -> {}\nFiles: {}\nInput files needed: {}".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()), self.inputDir, self.currentFiles, self.inputFiles))
        screenlock.release()

        for ext, val in self.inputFiles.items():
            if val is None:
                self.inputFiles[ext] = self.searchFileWithExtension(self.currentFiles, ext)

    def searchFileWithExtension(self, fileNames, extension):
        for f in fileNames:
            splitted = f.split('.')
            f_ext = splitted[-1]
            if extension == f_ext:
                return f
        return None

    def splitToList(self, string):
        if ',' in string:
            return string.split(',')
        else:
            return [string]



    def isInputComplete(self):
        for ext, val in self.inputFiles.items():
            if val is None:
                return False
        return True

    def cleanInputDirectory(self):
        filelist = listdir(self.inputDir)
        for f in filelist:
            remove(join(self.inputDir, f))

    def cleanDictionary(self):
        for ext, val in self.inputFiles.items():
            self.inputFiles[ext] = None



################################################################################
#
#
class ScriptExecutorCxx(ScriptExecutorBase):

    def __init__(self, config, iniSectionName):
        super().__init__(config, iniSectionName)

    def executeScript(self):
        print("CXX RUNNING SCRIPT!!!")






################################################################################
#
#
class ScriptExecutorPy(ScriptExecutorBase):

    def __init__(self, config, iniSectionName):
        super().__init__(config, iniSectionName)


    def executeScript(self):
        print("Py RUNNING SCRIPT!!!")
