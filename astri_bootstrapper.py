import os, time

def searchFileWithExtension(extension,files):
    for f in files:
        splitted = f.split('.')
        f_ext = splitted[-1]
        if extension == f_ext:
            return f
    return None

def searchFileWithSubstring(partialName, files):
    for f in currentFiles:
        if 'irf2' in f:
            return f
    return None

def searchEVT2(files):
    if len(files) > 0:
        for file in files:
            splitted = file.split('.')
            if len(splitted) >= 3:
                if file.split('.')[1] == 'lv2b' and file.split('.')[2] == 'ok':
                    print("--> evt2 found: {}".format(file))
                    return file
        return None

def poollingDirectory(dir, currFiles):
    time.sleep (5)
    print("Polling directory -> current files: {}".format(currFiles))

    after = set (os.listdir (path_to_watch))

    added = set([f for f in after if not f in currFiles])
    removed = set([f for f in currFiles if f not in after])

    if added: print("Added: {}".format(added))
    if removed: print("Removed: {}".format(removed))

    return added,removed




script_path = os.path.dirname(os.path.abspath(__file__))
folder_to_watch = "EVT2"
path_to_watch = "./"+folder_to_watch


# Deleting all content
files = os.listdir (path_to_watch)
for file in files:
    os.remove(script_path+'/'+folder_to_watch+'/'+file)

currentFiles = set (os.listdir (path_to_watch))

print("----> [Astri bootstrapper started!] <----\n")
while 1:

    newFiles,removedFiles = poollingDirectory(path_to_watch, currentFiles)

    currentFiles = currentFiles.union(newFiles)
    currentFiles = currentFiles - removedFiles


    if len(newFiles) > 0:

        # Check if an EVT2 file has been added
        evt2_filename = searchEVT2(currentFiles)

        # Processing the evt2
        if evt2_filename:

            filename = evt2_filename.split('.')[0]
            gti_filename = None
            irf_filename = None

            print("\nSearching for GTI: {}".format(gti_filename))

            gti_found = False
            while not gti_found:
                # search the corrisponding GTI
                gti_filename = searchFileWithExtension('lv0', currentFiles)
                if gti_filename:
                    print("GTI file found: {}".format(gti_filename))
                    gti_found = True
                else:
                    #print("GTI file NOT found. Searching for {}".format(gti_filename))
                    newFiles,removedFiles = poollingDirectory(path_to_watch, currentFiles)
                    currentFiles = currentFiles.union(newFiles)
                    currentFiles = currentFiles - removedFiles

                    continue


            print("\nSearching for IRF..")

            irf_found = False
            while not irf_found:
                # searching for the IRF
                irf_name = searchFileWithSubstring('irf2', currentFiles)
                if irf_name:
                    print("IRF file found: {}".format(irf_name))
                    irf_found = True
                    irf_filename = irf_name
                else:
                    #print("IRF file NOT found.")
                    newFiles,removedFiles = poollingDirectory(path_to_watch, currentFiles)
                    currentFiles = currentFiles.union(newFiles)
                    currentFiles = currentFiles - removedFiles
                    continue



            print("\n --> All files are present:\n  EVT2: {}\n  GTI:  {}\n  IRF:  {}\n\n".format(evt2_filename,gti_filename,irf_filename))


            # start the ASTRI pipeline
            astri_path = "/home/rt/ASTRI/astripipe_v0.2.5/astripipe/"
            astri_bootstrapper_path = "/home/rt/astri_bootstrapper"
            astri_configfile_model = astri_path+"astriana_gaussfit.par_model"
            astri_configfile = astri_path+"astriana_gaussfit.par"

            input_files_path = script_path+'/'+folder_to_watch+'/'

            # Update ASTRI config file
            updated_config = ""
            with open(astri_configfile_model) as af:
                content = af.readlines()
                for c in content:
                    if "evfile" in c:
                        updated_config += 'evfile,  s, a, "'+input_files_path+evt2_filename+'" , , , "EVT2 file or directory"\n'
                    elif "irf2_input_file" in c:
                        updated_config += 'irf2_input_file,  s, a, "'+input_files_path+irf_filename+'" , , , "IRF2 input FITS file"\n'
                    elif "gti_input_file" in c:
                        updated_config += 'gti_input_file,  s, a, "'+input_files_path+gti_filename+'" , , , "GTI input FITS file"\n'
                    else:
                        updated_config += c

            print("Aggiornato: \n",updated_config)
            with open(astri_configfile, "w") as ac:
                ac.write(updated_config)



            #command2 = "python ./astriana_gaussfit.py y "+script_path+'/'+folder_to_watch+'/'+evt2_filename+" "+script_path+'/'+folder_to_watch+'/'+irf_filename+" "+script_path+'/'+folder_to_watch+'/'+gti_filename
            command2 = "python ./astriana_gaussfit.py"


            print("\n----> Starting analysis with:\n  {}\n\n".format(command2))

            os.chdir(astri_path)
            print(os.getcwd())

            os.system(command2)

            os.chdir(astri_bootstrapper_path)
            print(os.getcwd())


            print("\n----> ASTRI analysis finished!\n")

            # Removing EVT2 and GTI
            os.remove(script_path+'/'+folder_to_watch+'/'+evt2_filename)
            os.remove(script_path+'/'+folder_to_watch+'/'+gti_filename)
            currentFiles.remove(evt2_filename)
            currentFiles.remove(gti_filename)



    """
    cp ../real_data/astri_000_41_001_00001_R_000000_001_0201.lv2b ./astri_000_41_001_00001_R_000000_001_0201.lv2b.ok
    cp ../real_data/astri_000_41_001_00001_R_000000_001_0601.lv0 ./
    cp ../real_data/irf2_C3.lv2b ./
    """
      #
