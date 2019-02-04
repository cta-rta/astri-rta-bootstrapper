import subprocess
from os import listdir
from os.path import isfile, join
from shutil import copyfile
from time import sleep
import os, shutil


def delete_directory_contents(path_to_folder):
    for the_file in os.listdir(path_to_folder):
        file_path = os.path.join(path_to_folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print("Error: ", e)
            exit(1)

def copy_lv0(lv0_folder_path, lv0_dest_path):
    lv0_files = [f for f in listdir(lv0_folder_path) if isfile(join(lv0_folder_path, f)) and '.lv0' in f]
    for f in lv0_files:
        try:
            copyfile(lv0_folder_path+"/"+f, lv0_dest_path+"/"+f)
        except Exception as e:
            print("Error: ",e)
            exit(1)

def copy_irf(irf_src, irf_dest):
    try:
        copyfile(irf_src, irf_dest)
    except Exception as e:
        print("Error: ",e)
        exit(1)



processes_threshold = 30
sleep_time = 3
delete_existing_files = True


command = "ssh cta@merlin.iasfbo.inaf.it squeue | wc -l"
input_files_path = "/home/cta/Baroncelli_development/ASTRI_DL2/data_lv2a"
dest_files_path = "/home/cta/Baroncelli_development/ASTRI_DL2/output/dl2a.out"
number_of_files = len([f for f in listdir(input_files_path) if isfile(join(input_files_path, f)) and '.lv2a' in f])
#print("input_files: ", input_files)

if delete_existing_files:
    delete_directory_contents(dest_files_path)
    delete_directory_contents("/home/cta/Baroncelli_development/ASTRI_DL2/output/dl2b.out")
    delete_directory_contents("/home/cta/Baroncelli_development/ASTRI_DL2/output/dl3.out")
    copy_lv0("/home/cta/Baroncelli_development/ASTRI_DL2/data_lv2b/EVT2b/dummy", "/home/cta/Baroncelli_development/ASTRI_DL2/output/dl2b.out")
    copy_irf("/home/cta/Baroncelli_development/ASTRI_DL2/data_lv2b/IRF2/irf2_C6.lv2b", "/home/cta/Baroncelli_development/ASTRI_DL2/output/dl2b.out/irf2_C6.lv2b")


file_index = 0

while( file_index <= number_of_files-1 ):

    input_file = "astri_000_41_001_00001_R_00000"+str(file_index)+"_001_0201.lv2a"

    # count how many SLURM processes are running
    completedProcess = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if completedProcess.stderr:
        print("Error ({}): {}".format(completedProcess.returncode, completedProcess.stderr.decode("utf-8")))
        exit(1)

    number_of_processes = int(completedProcess.stdout.decode("utf-8")) - 1
    print("number_of_processes: ", number_of_processes)


    if number_of_processes < processes_threshold:

        try:
            copyfile(input_files_path+"/"+input_file, dest_files_path+"/"+input_file)

        except Exception as e:
            print("Error: ",e)
            exit(1)

        file_index += 1

    sleep(sleep_time)
