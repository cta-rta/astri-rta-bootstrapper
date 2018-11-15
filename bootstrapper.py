import configparser
from os import putenv, system
from queue import Queue
from ScriptExecutor import ScriptExecutorPy, ScriptExecutorCxx


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
