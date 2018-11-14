import configparser
from abc import ABC, abstractmethod
from os.path import isdir
from os import listdir, remove, system
from os.path import join
from time import sleep, gmtime, strftime
import threading
from threading import Semaphore
import subprocess

screenlock = Semaphore(value=1)

class ScriptExecutorBase(ABC):

    @abstractmethod
    def executeScript(self):
        pass

    def __init__(self, config, iniSectionName):

        self.executorName = config[iniSectionName]['name']

        self.inputDir = config['GENERAL']['dataPath']+'/'+config[iniSectionName]['inputDir']
        self.tempOutputDir = config['GENERAL']['tempOutputDir']+'/'+config[iniSectionName]['outputDir']    # do NOT invert tempOutputDir and outputDir!
        self.outputDir = config['GENERAL']['dataPath']+'/'+config[iniSectionName]['outputDir']

        self.outputExt = config[iniSectionName]['outputExtension']
        self.outputTempName = 'out.'+config[iniSectionName]['outputExtension']+'.tmp'

        self.searchForExtsList = self.splitToList(config[iniSectionName]['inputExtensions'])

        self.executableName = config[iniSectionName]['exeName']
        self.executable = config[iniSectionName]['exeDir']+'/'+config[iniSectionName]['exeName']
        self.sleepSec = config[iniSectionName]['sleepSec']
        self.debug = config.getboolean('GENERAL','debug')
        self.parFileName = config[iniSectionName]['parFileName']
        self.parFile = config[iniSectionName]['parFileDir']+'/'+config[iniSectionName]['parFileName']
        self.canContinue = True
        self.inputFilesFound = False

        # Dictionary object -> { extension: filepath, ..  }
        self.inputFiles = {}
        for ext in self.searchForExtsList:
            self.inputFiles[ext] = None

        print("\nExecutor started! Info:")
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

            screenlock.acquire()

            # Script phase
            system('cp '+self.parFile+' ./') # Copy par file  -> create a function that move the par file and then check if the file is present
            system('mkdir -p '+self.tempOutputDir) # Create temp folder for temporary output

            self.executeScript() # The output files are written in a temp directory


            # Clean phase
            system('rm '+self.parFileName)
            self.cleanDirectory(self.inputDir)
            self.cleanDictionary()
            self.inputFilesFound = False

            screenlock.release()


            """
            TODO

            Errori:
            /home/cta/Baroncelli_development/ASTRI_DL2/astrirta_install/bin/astrireco_arr: /home/cta/Baroncelli_development/ASTRI_DL2/astrirta_install/bin/astrireco_arr: cannot execute binary file
            cp: impossibile eseguire stat di "/home/cta/Baroncelli_development/astri-rta-bootstrapper/tmp/lv2b.out/out.lv2b.tmp": File o directory non esistente

            Usare subprocess per catturare gli errori e creare una funzione wrapper per le system calls
            """



    ###########################################################################
    # Utility functions
    #
    def printInfo(self):
        print("My name is: {} \nI watch the dir: {}\nI look for: {}\nI run: {}".format(self.executorName,self.inputDir,self.searchForExtsList,self.executable))

    def searchForInputFiles(self):

        sleep(int(self.sleepSec))

        self.currentFiles = listdir (self.inputDir)

        screenlock.acquire()
        if self.debug:
            print("\n[{} {}] Polled directory -> {}\nFiles: {}\nInput files needed: {}".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()), self.inputDir, self.currentFiles, self.inputFiles))
        else:
            print("\n[{} {}] {}".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()),self.inputFiles))
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

    def cleanDirectory(self, dir):
        filelist = listdir(dir)
        for f in filelist:
            remove(join(dir, f))

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

        command = 'bash '+self.executable+' '+self.inputFiles['lv2a']+' '+self.tempOutputDir+'/'+self.outputTempName

        print("\n[{} {}] ----> Running script with:\n  - {}".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()), command))

        system(command)

        system('cp '+self.tempOutputDir+'/'+self.outputTempName+' '+self.outputDir) # the files are moved into the output directory

        print("\n[{} {}] ----> Script {} finished!".format(self.executorName, strftime("%Y-%m-%d %H:%M:%S", gmtime()), self.executableName))


        """
        os.chdir(astri_path)
        print(os.getcwd())
        system(command2)
        os.chdir(astri_bootstrapper_path)
        print(os.getcwd())
        """





################################################################################
#
#
class ScriptExecutorPy(ScriptExecutorBase):

    def __init__(self, config, iniSectionName):
        super().__init__(config, iniSectionName)


    def executeScript(self):
        print("Py RUNNING SCRIPT!!!")
