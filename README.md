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
  * It polls the input directory until it finds all the files that it needs to launch its analysis script.
  * It copies the par file within its directory
  * It creates a temporary folder to store the temporary output of the analysis script.
  * It executes the analysis script defining the needed environment variables.
  * When the analysis script is terminated, it moves its temporary output to the right destination directory (there will be another ScriptExecutor polling in that directory)
  * It deletes the par file
  * It deletes the input files
  * It starts to poll again

If any system call raise any error, the ScriptExecutors will quit.

## Assumptions
* Each script produces only one file

## Improvements
* Using PFILES env var and not copy the par files into the bootstrapper directory
