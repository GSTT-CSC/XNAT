#!/usr/bin/env python

'''import-via-restapi.py

Usage:
    import-via-restapi.py CSV PROJECT PACSID

Options:
   CSV
   PROJECT
   PACSID

'''

import os
import sys
from docopt import docopt
import csv
import time
import csv
import json
import modules.xnat_utils as svr

xnat = svr.xnat_utils()

version = "1.0"
args = docopt(__doc__, version=version)
csv_file = args.get('CSV')
project = args.get('PROJECT')
pacs_id = args.get('PACSID')

## read csv file to get subject mappings:
subject_mapping = dict()
session_mapping = dict()
with open(csv_file) as csvfile:
    sessions = csv.DictReader(csvfile, delimiter=',')
    for row in sessions:
        if 'Accession Number' in row:
            subject_mapping[row['Accession Number']] = row['Subject']
            session_mapping[row['Accession Number']] = row['Session']
        else:
            subject_mapping[row['Patient ID']] = row['Subject']
            session_mapping['{}{}'.format(row['Patient ID'], row['Study Date'])] = row['Session']

## print all subjects and sessions for data quality check
print(subject_mapping)
print(session_mapping)

url = '/xapi/pacs/{}'.format(pacs_id)
pacs = xnat.get(url)
aet = xnat.extract_values(pacs, 'aeTitle')[0]
port = xnat.extract_values(pacs, 'queryRetrievePort')[0]
aet = 'XNAT'
port = '8105'
print(pacs)
print('##### Querying PACS')

batch = xnat.postdqr('/xapi/dqr/query/batch', csv_file, pacs_id)

print('###########')
for studies in batch:
    print('##### Study:')

    for study in studies['studies']:
        print(json.dumps(study, indent=4, sort_keys=True))
        print("Importing Study: {}  - date: {}".format(study['studyId'], study['studyDate']))
        try:
            search_list = []

            search_list.append('\"studyInstanceUid\":  \"{}\" '.format(study['studyInstanceUid']))
            search_list.append('\"accessionNumber\":  \"{}\" '.format(study['accessionNumber']))
            search_list.append('\"studyDate\":  \"{}\"  '.format(study['studyDate']))

            relabelmap = "{{  \"Subject\": \"{}\", \"Session\": \"{}\"   }}".format(
                subject_mapping[study['accessionNumber']], session_mapping[study['accessionNumber']])
            search_list.append('\"relabelMap\":   {}  '.format(relabelmap))

            search_query = ",".join(search_list)

            searchterm = '{{ \"aeTitle\": \"{}\",  \"forceImport\": true,  \"pacsId\": {},  \"port\": {},  \"projectId\": \"{}\",  \"studies\": [  {{     {}   }} ] }}'.format(
                aet, pacs_id, port, project, search_query)
            print(json.dumps(searchterm, indent=4, sort_keys=True))
            sectra_uid = "1.2.752.24.7*,"
            print(searchterm)
            attempts = 0
            while attempts < 50:
                r = xnat.dqr_retrieve('/xapi/dqr/import', searchterm)
                print(json.dumps(r.text, indent=4, sort_keys=True))
                if 'There was a problem' in r.text:
                    print('There was a problem with {}'.format(study['accessionNumber']))
                    attempts += 1
                    time.sleep(120)
                else:
                    break
        except Exception as e:
            print('Error importing {}: {} '.format(study['accessionNumber'], e))
        print('############################')
        time.sleep(60)
xnat.close()
