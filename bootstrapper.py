import configparser
from os import putenv, system
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
sections.remove('ENVIRONMENT')
print("Scripts:\n{}".format(sections))

################################################################################
# Define environment variables
#
envVars = config.options('ENVIRONMENT')
print("\nEnvironment variables:")
for varName in envVars:
    varNameUpper = varName.upper()
    varValue = config.get('ENVIRONMENT',varNameUpper)
    putenv(varNameUpper, varValue)
    system("echo "+varNameUpper+"=$"+varValue)

print("""
--------------------------------------------------------------------------------
""")

################################################################################
# Executors
#
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
