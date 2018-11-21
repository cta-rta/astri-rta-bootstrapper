# astri-rta-bootstrapper

## Prerequisities
Python 3.6.6

## Starting the script
```bash
python boostrapper.py
```
## Description
* The bootstrapper.py read the config file and starts ScriptExecutors.
* Each ScriptExecutor use a thread to run its START_WORK() main function.
  * It checks if the directories and files specified in the configuration file exist. Then, it enters in a while loop.
  * It polls the input directory until it finds all the files that it needs to launch its analysis script. If there exist more than one input file of the same type, the ScriptExecutor will consume the oldest one.
  * It copies the par file within its directory.
  * It creates a temporary folder to store the temporary output of the analysis script.
  * It defines the environment variables needed and then executes the analysis script .
  * When the analysis script is terminated, it moves its temporary output to the destination directory (there will be another ScriptExecutor polling in that directory)
  * It deletes the par file
  * It deletes the input files or marks them as 'consumed'
  * It starts to poll again

## Logging
Each ScriptExecutor has its own log file, located under the logs/ directory.

## Termination
If any system call raise any error, all the ScriptExecutors will quit, reporting the error.

## Assumptions
* All the scripts use the PAR input sysyem.
* All the different input files needed for the analysis script executions must be located into the same directory.
* Each script asks where to save the output file (at least one file)

## Configuration file
The configuration file has a 'general' section and one 'script-specific' section for each script.
* [required] => the field value must be set
* [optional] => the field value can be blank

### General section
* debug: [yes/no] [required] if yes all the logs will be output on the console
* keepInputFiles: [required] if yes the input files are not deleted once used but they remain in the input directory

### Script-specific section
For each script you want to handle, you need to write a script-specific section with the following keys:

* name = [required] name of the ScriptExecutor, could be anything
* language = [python/c++] [required] script programming language
* interpreter = [optional] full path to language interpreter (e.g. /home/cta/.conda/envs/astripipe/bin/python)
* sleepSec = [required] the ScriptExecutor will sleep for 'sleepSec' seconds after each directory poll

* exeDir = [required] full path to the directory that contains the script executable (should NOT end with '/')
* exeName = [required] the script executable name (e.g. astriana.py)

* inputDir = [required] full path to the directory that contains the input files (should NOT end with '/')

* scriptInputsDict = [Python dictionary] [required] Here are defined all the inputs you want to give to the script. There are two types of input: the 'inputfile' type (the ScriptExecutor will look for it) and the 'output' type -> its value is passed through the configuration file. Each dictionary key has a incremental integer number that corrisponds to the order with wich you want to give the inputs. The corrisponding value is another python dictionary that describe the input (lets call it value-dictionary). The value-dictionary contains several parameters:
  * type: [inputfile/output] -> the 'inputfile' type refers to an actual file that the ScriptExecutor needs to run the script. The input file is  searched using 'ext', 'pattern' and 'excludepattern' parameters. The type 'output' refers to the filename of the analysis script output. Its value MUST be specified through the 'value' parameter.
  * ext: file extension. You must omit the '.' (e.g. 'lv2b')
  * pattern: if a 'pattern' string value is provided, the ScriptExecutor will looks for a filename with extension 'ext' and containing the 'pattern' in its filename
  * excludepattern: -> if a 'excludepattern' string value is provided, the ScriptExecutor will looks for a filename with extension 'ext' and NOT containing the 'excludepattern' in its filename
  * value: the actual string value if type=output

```python
scriptInputsDict = { '1':{'type':'inptufile', 'ext':'lv2a', 'pattern':'', 'exludepattern':'irf', 'value':''},
                     '2':{'type':'output', 'ext':'', 'pattern':'', 'exludepattern':'', 'value':'/home/user/pipeoutput/dl3.out/astri.out.lv3'}
                  }
```

* parFileDir = [required] full path to the directory that contains the par file (should NOT end with '/')
* parFileName = [required] par filename
* updateParValuesWith = [Python Dictionary] If the dictionary is not empty ({}), the ScriptExecutor will modify the par file. The dictionary is a mapping telling what field must be updated (keys) with the inputs (values).
Example:
```python
updateParValuesWith = [required] {'evfile':'1', 'outfile':'2'}
```


* envvars = [required] [Python Dictionary] It contains all the environment variables that are needed in order to run the script.
Example:
```python
envvars = { 'PYTHONPATH':'/home/user/pythonlib:/home/user/pythonlib2', 'PFILES':'/home/user/c++project/parfiles'}
```

### Blank configuration file
```bash
[GENERAL]
debug =  ..
keepInputFiles = ..

[script_1]
name = ..
language = ..
interpreter =
sleepSec = ..

exeDir = ..
exeName = ..

inputDir = ..
scriptInputsDict = {}

parFileDir = ..
parFileName = ..
updateParValuesWith = {}

envVars = {}
```
