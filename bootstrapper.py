import configparser
from ScriptExecutor import *

print("""
                __
               / _)  Pipeline Boostrapper
        .-^^^-/ /
    __/       /
   <__.|_|-|_|

""")

config = configparser.ConfigParser()
config.read('conf.ini')

if config['GENERAL'].getboolean('debug'):
    debug = True

sections = config.sections()
sections.remove('GENERAL')

print(sections)

executors = []


for sectionName in sections:
    if config[sectionName]['language'] == 'c++':
        executors.append(ScriptExecutorCxx(config, sectionName))

    elif config[sectionName]['language'] == 'python':
        executors.append(ScriptExecutorPy(config, sectionName))

    else:
        print("Language not supported")
        exit()


for executor in executors:
    #executor.printInfo()
    executor.START_WORK()
