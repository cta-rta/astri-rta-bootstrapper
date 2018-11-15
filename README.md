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
  * It copies the par file within its directory
  * It creates a temporary folder to store the temporary output of the analysis script.
  * It executes the analysis script defining the needed environment variables.
  * When the analysis script is terminated, it moves its temporary output to the right destination directory (there will be another ScriptExecutor polling in that directory)
  * It deletes the par file
  * It deletes the input files
  * It starts to poll again

If any system call raise any error, the ScriptExecutors will quit.

## Assumptions
* Each script produces only one file -> TO MODIFY!!
* All the different input files needed for the analysis script executions must be located into the same directory.
* The input files that are used for an analysis script execution, are deleted when the script ends. -> TO MODIFY!! Mark them as 'used' or move them.
* [!] A script can take in input only one file of a specific extension.
* [!] The modification of the par file functionality works if and only if the input files have different extensions.

## Possible improvements
* Use PFILES env var instead of configuration option for locating the par file.
* Add to inputExtensions configuration option the [\*ext] signature to eat all the file with ext extension
* Add to inputExtensions configuration option [ext,ext] signature to eat two file (the oldest) with the same extension
