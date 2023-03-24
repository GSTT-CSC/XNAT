#!/usr/local/bin/python3

'''SeriesDescription_Extractor.py

Usage:
    python3 SeriesDescription_Extractor.py PATH

Options:
    PATH

'''

import os
import pydicom
import sys

path_to_folder = sys.argv[1]

print('Starting folder scan')

my_dir = path_to_folder   # Paste the folder path to root folder you want to interogate

f = open("SeriesDescriptors.txt", "w")    # Creates new text file where result will be saved

for path, sub_dirs, files in os.walk(my_dir):  #Traverses directory recursively through any/all sub folders
    for file in files:
        if file.endswith(".dcm"):
            file_path = os.path.join(path, file)  #Joins file to path statement
            fn = pydicom.dcmread(file_path)
            a = [fn.PatientName, fn.PatientID, fn.SeriesNumber,fn.SeriesDescription]   #Output information want to display (file name and series descr tag)
            print(a)
            f.writelines("%s\n" % a)          #Saves results in text file

print('done writing into file')
print(f)
