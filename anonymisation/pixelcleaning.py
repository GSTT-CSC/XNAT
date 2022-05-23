# This script is used to perform burnt-in pixel scrubbing from ultrasound data
# To run from terminal, run the following:
# python3 pixelcleaning.py INPUT_FOLDER


from deid.dicom import DicomCleaner
import os
import sys

if len(sys.argv) != 2:
    raise Exception('Wrong number of arguments!')

base = sys.argv[1]

client = DicomCleaner() # do we need to define this before the below?
client = DicomCleaner(base + '/iFINDclean/')

ext = ('.dcm')
dicom_files = []

for root, folders, files in os.walk(base):
    for file in files:
        fullpath = os.path.abspath(os.path.join(root, file))
        dicom_files.append(fullpath)
        print(fullpath)
        if file.endswith(ext):
            client.detect(fullpath)
            print('done detect')
            client.clean()
            print('done clean')
            client.save_dicom()
            print('done save')
        else:
            continue

print('all done now')
