# DMCTK upload script WIP
'''modify_dicoms
sdfsd

Usage:
    modify_dicoms.py ACCNUM SUBJECT SESSION PROJECT IN_DIR

Options:
    ACCNUM
    SUBJECT
    SESSION
    PROJECT
    IN_DIR


'''


import pydicom
import os
from docopt import docopt
import time
import shutil

version = "1.0"
args = docopt(__doc__, version=version)
acc_num = args.get('ACCNUM')
session_label = args.get('SESSION')
subject_label = args.get('SUBJECT')
project = args.get('PROJECT')
in_dir=args.get('IN_DIR')


found_folders=[]
static=False
for folder in os.listdir(in_dir):
    #find folder with 
    full_path=os.path.join(in_dir,folder)    
    found=False
    for fl in os.listdir(full_path):
        try:
            with open(os.path.join(full_path,fl), 'rb') as f:
                dataset = pydicom.dcmread(f)
                if "AccessionNumber" in dataset and not found:
                    if acc_num in dataset.AccessionNumber:
                        found_folders.append(full_path)
                        found=True
                else:
                    break

        except Exception as e:
            print(e)

print(found_folders)
folder=1
for full_path in found_folders:
    print("Found session {} sub:{} ses:{} in folder: {}".format(acc_num, subject_label, session_label, full_path))
   
    
    while not static:    
        size_of_files1 = sum(os.path.getsize(os.path.join(full_path, f)) for f in os.listdir(full_path))
        time.sleep(1000)
        size_of_files2 = sum(os.path.getsize(os.path.join(full_path, f)) for f in os.listdir(full_path))
        if size_of_files1 == size_of_files2 and size_of_files1 > 0:
            print("Session Static - {} ".format(session_label))
            for fl in os.listdir(full_path):
                try:
                    with open(os.path.join(full_path, fl), 'rb') as f:
                        dataset = pydicom.dcmread(f)
                        #print('{} - {}'.format(dataset.PatientName, subject_label))
                        dataset.PatientName = subject_label
                        dataset.PatientID = session_label
                        dataset.StudyDescription = project
                        #print("Saving file {}/{}".format(full_path, fl))
                        dataset.save_as(os.path.join(full_path,fl))
                                        
                except Exception as e:
                    print(e)
            static=True
            print('Moving session')
            shutil.move(full_path,os.path.join('/xnat-data/import_data/', session_label))

