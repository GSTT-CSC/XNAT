#!/usr/bin/env python

'''import-dqr.py

Usage:
    ./REST-api-get-data.sh CSV.csv PACSID OUTPUT.json

Options:
   CSV
   PACSID
   OUTPUT

The output file will be created in xnat-data/scripts/import-dqr folder
'''

import os
import sys
from docopt import docopt
import csv
import json
import modules.xnat_utils as svr
#import fnmatch
import io

xnat = svr.xnat_utils()

version = "1.0"
args = docopt(__doc__, version=version)
csv_file = args.get('CSV')
pacs_id = args.get('PACSID')
output_file = args.get('OUTPUT')

url = '/xapi/pacs/{}'.format(pacs_id)

#returns json

pacs = xnat.get(url)
aet = xnat.extract_values(pacs, 'aeTitle')[0]
port = xnat.extract_values(pacs, 'queryRetrievePort')[0]

aet='XNAT'
port = '8105'
print('##### Querying PACS')

batch = xnat.postdqr('/xapi/dqr/query/batch', csv_file, pacs_id)

with io.open(output_file, 'w', encoding='utf-8') as f:
	f.write(json.dumps(batch, indent=4, sort_keys=True))

print('done writing into file')

xnat.close()
