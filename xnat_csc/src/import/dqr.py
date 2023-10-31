#!/usr/bin/env python3

'''dqr.py

Usage:
    dqr.py CSV PROJECT ISSUBJECT

Options:
    CSV
    PROJECT
    ISSUBJECT     PatientID,StudyDate csv file


'''

import pydicom
import os
from docopt import docopt
import time
import shutil
import csv
import subprocess
import shlex
from datetime import datetime, timedelta
import sys

version = "1.0"
args = docopt(__doc__, version=version)


csv_file = args.get('CSV')
project = args.get('PROJECT')
subject_level = args.get('ISSUBJECT')
pacs_ip = '172.31.2.61'
pacs_port = '7958'
aec = 'QR_SCP_XNAT'
aem = 'XNAT'
in_dir = '/xnat-install/incoming_data'
wait = 90
batch_size = 5
### requires a dicom receiver


def import_incoming(studies):
    sc = 0
    print('#### IMPORTING BATCH - {} studies ####'.format(len(studies)))
    for s in studies:
        time.sleep(20)
        print(sc)
        study_uid = studies[sc]["uid"]
        subject_label= studies[sc]["subject_label"]
        session_label = studies[sc]["session_label"]
        sc += 1
        found_folders = []
        static = False

        dt = datetime.now()
        #might be day after.....
        today = dt.strftime("%Y%m%d")
        yt = datetime.today() - timedelta(days=1)
        yesterday = yt.strftime("%Y%m%d")

        #print(yesterday)
        #print(today)
        attempts = 1
        found = False

        while not found and attempts < 20:
            for folder in os.listdir(in_dir):
                if study_uid in folder and not found:
                    #print('Searching in directory:', folder, ' Attempt:', attempts)
                    # find folder
                    full_path = os.path.join(in_dir, folder)
                    found_folders.append(full_path)
                    found = True
                    #for fl in os.listdir(full_path):
                    #    try:
                    #        with open(os.path.join(full_path, fl), 'rb') as f:
                    #            dataset = pydicom.dcmread(f)
                    #            if study_uid in dataset.StudyInstanceUID:
                    #                found_folders.append(full_path)
                    #                found = True
                    #                print('Found session in', folder)
                    #                break
                    #    except Exception as e:
                    #        print(e)
            time.sleep(10)
            attempts += 1

        if attempts == 20:
            print("ERROR: could not find session after move request. {}".format(session_label))
        else:
            print(found_folders)
            for full_path in found_folders:
                static=False
                print("Found session - sub:{} ses:{} in folder: {}".format(subject_label, session_label, full_path))
                while not static:
                    size_of_files1 = sum(os.path.getsize(os.path.join(full_path, f)) for f in os.listdir(full_path))
                    time.sleep(wait)
                    size_of_files2 = sum(os.path.getsize(os.path.join(full_path, f)) for f in os.listdir(full_path))
                    if size_of_files1 == size_of_files2 and size_of_files1 > 0:
                        print("Session Static - {} ".format(session_label))
                        for fl in os.listdir(full_path):
                            try:
                                with open(os.path.join(full_path, fl), 'rb') as f:
                                    dataset = pydicom.dcmread(f)
                                    # print('{} - {}'.format(dataset.PatientName, subject_label))
                                    dataset.PatientName = subject_label
                                    dataset.PatientID = session_label
                                    dataset.StudyDescription = project
                                    # print("Saving file {}/{}".format(full_path, fl))
                                    dataset.save_as(os.path.join(full_path, fl))

                            except Exception as e:
                                print(e)
                        static = True
        
            for full_path in found_folders:
                print('Moving folder to XNAT:', full_path)
                shutil.move(full_path, os.path.join('/xnat-data/import_data/', session_label))


print('########## DQR.PY DQR IMPORTER #########')
if 'True' in subject_level or '1' in subject_level:
    subject_level = True
    print('Reading csv file {} - searching by PatientID, StudyDate'.format(csv_file))
else:
    subject_level = False
    print('Reading csv file {} - searching by Accession Number'.format(csv_file))

uids = {}
uidc = 0

with open(csv_file, newline='') as csvfile:
    session_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in session_reader:
        print('### SEARCHING: ', row)
        cmd = ''
        success = False
        while not success:
            if subject_level:
                hospital_number = row[0]
                study_date = row[1]
                subject_label = row[2]
                session_label = row[3]

                cmd = 'findscu -aet XNAT -aec {} -v -S -k 0008,0052=STUDY -k 0010,0020="{}" -k 0008,0020="{}"  {} {}   -k 0020,000D'.format(aec,row[0], row[1], pacs_ip, pacs_port)
                cmd = shlex.split(cmd)
            else:
                acc_num = row[0]
                subject_label = row[1]
                session_label = row[2]

                cmd = 'findscu -aet XNAT -aec {} -v -S -k 0008,0052=STUDY -k 0008,0050="{}"  {} {}   -k 0020,000D'.format(aec,row[0], pacs_ip, pacs_port)
                cmd = shlex.split(cmd)

            out = '{}'.format(subprocess.run(cmd,  capture_output=True, text=True))
            print(out)
            if 'Association Rejected' in out:
                #urghhh have to wait a while before allowing more
                print('Association Rejected - too many calls? Waiting 2 minutes...')
                time.sleep(120)
            else:
                success = True
        print('   ')
        for line in out.split('nI'):

            line_str = '{}'.format(line.rstrip())
            if "0, 0 StudyInstance" not in line_str and 'StudyInstance' in line_str:
                print('FOUND line ', line_str)
                # complete guess
                study_uid = line_str.split(' ')
                study_uid = study_uid[3].replace('[','').replace(']','').replace('\\x00','')
                print(study_uid)

                cmd = 'movescu -aet XNAT -aec {} -aem {} -k 0008,0052=STUDY -k 0020,000D="{}" {} {}'.format(aec, aem,study_uid, pacs_ip, pacs_port)
                cmd = shlex.split(cmd)
                
                #sucess = False
                
                #while not success:
                #    #proc = subprocess.Popen(cmd)
                #    out = '{}'.format(subprocess.run(cmd,  capture_output=True, text=True))
                #    if 'Association Rejected' in out:
                #        print('Association Rejected.... trying again in 5 minutes')
                #        time.sleep(300)
                #    else:
                #        success=True
                proc = subprocess.Popen(cmd)
                #print('process ran')

                study_uid = {"uid" : study_uid, "subject_label" : subject_label, "session_label" : session_label}
                uids[uidc] =  study_uid
                uidc += 1
                print('uid:', study_uid, ' uidc:', uidc, ' uids:', uids)

                if uidc == batch_size:
                    #import in batches on 10
                    #print(uids)
                    import_incoming(uids)
                    uids = {}
                    uidc = 0
                else:
                    time.sleep(10)

# for any leftover not in batches of 10
import_incoming(uids)




