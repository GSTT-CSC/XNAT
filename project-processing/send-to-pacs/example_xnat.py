#!/usr/bin/env python

'''import-dqr.py

Usage:
    import-dqr CSV PROJECT PACSID DESCRIPTION

Options:
   CSV
   PROJECT
   PACSID
   DESCRIPTION

'''

import os
import sys
from docopt import docopt
import csv
import time
import csv
import json
# import pandas as pd
import modules.xnat_utils as svr
import fnmatch

xnat = svr.xnat_utils()

version = "1.0"
args = docopt(__doc__, version=version)
csv_file = args.get('CSV')
project = args.get('PROJECT')
pacs_id = args.get('PACSID')
study_desc = args.get('DESCRIPTION')

## read csv file to get subject mappings:
# either accession number OR subject ID/SudyDate (what if multiple...?)
subject_mapping = dict()
session_mapping = dict()
with open(csv_file) as csvfile:
    sessions = csv.DictReader(csvfile, delimiter=',')
    for row in sessions:
        # print(row)
        if 'Accession Number' in row:
            # print(row['Accession Number'], row['Subject'], row['Session'])
            subject_mapping[row['Accession Number']] = row['Subject']
            session_mapping[row['Accession Number']] = row['Session']
        else:
            subject_mapping[row['Patient ID']] = row['Subject']
            session_mapping['{}{}'.format(row['Patient ID'], row['Study Date'])] = row['Session']

print(subject_mapping)
print(session_mapping)
# sys.exit()


url = '/xapi/pacs/{}'.format(pacs_id)
# returns json
pacs = xnat.get(url)
aet = xnat.extract_values(pacs, 'aeTitle')[0]
port = xnat.extract_values(pacs, 'queryRetrievePort')[0]
# ummm.... change to 8105
# aet='XNAT'
aet = 'XNAT'
port = '8105'
print(pacs)
print('##### Quering PACS')
# See if only one study fits criteria....? Need to break up csv?
batch = xnat.postdqr('/xapi/dqr/query/batch', csv_file, pacs_id)
# print(batch)
# print(json.dumps(batch, indent=4, sort_keys=True))
# sys.exit()
print('###########')
for studies in batch:
    print('##### Study:')

    for study in studies['studies']:
        print(json.dumps(study, indent=4, sort_keys=True))
        print("Importing Study: {}  - date: {}".format(study['studyId'], study['studyDate']))
        try:
            # do in batches?
            search_list = []

            search_list.append('\"studyInstanceUid\":  \"{}\" '.format(study['studyInstanceUid']))
            search_list.append('\"studyId\":   \"{}\"  '.format(study['studyId']))
            # search_list.append('\"studyDescription\":  \"{}\" '.format(descriptions[num]))
            search_list.append('\"accessionNumber\":  \"{}\" '.format(study['accessionNumber']))
            search_list.append('\"studyDate\":  \"{}\"  '.format(study['studyDate']))
            # search_list.append('\"modalitiesInStudy\":   \"{}\"  '.format(mods[num]))
            search_list.append('\"patient\":   \"{}\"  '.format(study['patient']))

            relabelmap = "{{  \"Subject\": \"{}\", \"Session\": \"{}\"   }}".format(
                subject_mapping[study['accessionNumber']], session_mapping[study['accessionNumber']])
            search_list.append('\"relabelMap\":   {}  '.format(relabelmap))

            search_query = ",".join(search_list)

            # port 8105
            searchterm = '{{ \"aeTitle\": \"{}\",  \"forceImport\": true,  \"pacsId\": {},  \"port\": {},  \"projectId\": \"{}\",  \"studies\": [  {{     {}   }} ] }}'.format(
                aet, pacs_id, port, project, search_query)
            print(json.dumps(searchterm, indent=4, sort_keys=True))
            sectra_uid = "1.2.752.24.7*,"
            # searchterm = searchterm.replace(sectra_uid, '')
            # print(searchterm)
            # sys.exit()
            # for ids in searchterm['studies']['seriesIds']:
            #    print('Sries IDs: {}', ids)
            # sys.exit()
            # for i in xrange(len(searchterm)):
            #    if fnmatch(searchterm[i]['seriesIds'], sectra_uid):
            #        print('Excluding scan: {}'.format(searchterm[i]['seriesIds']))
            #         obj.pop(i)

            attempts = 0
            while attempts < 50:
                r = xnat.dqr_retrieve('/xapi/dqr/import', searchterm)
                print(json.dumps(r.text, indent=4, sort_keys=True))
                if 'There was a problem' in r.text:
                    print('There was a problem with {}'.format(study['accessionNumber']))
                    attempts += 1
                    time.sleep(120)
                    # made no difference
                    # xnat.close()
                    # xnat = svr.xnat_utils()
                else:
                    break
        except Exception as e:
            print('Error importing {}: {} '.format(study['accessionNumber'], e))
        print('############################')
        time.sleep(60)
xnat.close()
