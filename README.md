# astri-rta-bootstrapper

## Instructions

* Activate the astri_pipe virtualenv
* starts the deamon with python astri_bootstrapper.py

The deamon pools every 5 second the EVT2 directory,  waiting for 3 files with the following extensions:
* .lv2b.ok
* .lv0
* irf2_C3.lv2b

When the files are present in the directory, the deamon starts the astri pipeline and, at the end of the computation, it delets the .lv2b.ok and .lv0 files.
