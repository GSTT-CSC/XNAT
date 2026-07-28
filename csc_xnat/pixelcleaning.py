# This script performs burnt-in pixel scrubbing from ultrasound images
# using the de.id library

# 21072026 Last updated by Kristina Zeljic
# Updates: added RGB conversion, added optional interactive prompt, added validation
# of input directory, removed hardcoding, improved file filtering, and added relative path handling.

# NOTE:
# RGB images are converted to grayscale in-place before cleaning.
# This modifies the original file, but is acceptable as this script is
# intended to run on copied datasets, not original data in the XNAT archive.

# Usage:
# Command line:
#     python3 pixelcleaning.py <INPUT_FOLDER>

# Interactive:
#     python3 pixelcleaning.py
#     (you will be prompted for the input folder)    

# Input: Folder containing DICOM files
# Output: Cleaned DICOM files saved under: <INPUT_FOLDER>/clean/

from deid.dicom import DicomCleaner
import os
import sys
import pydicom
import numpy as np

# -------------------------Input handling--------------------------
if len(sys.argv) == 2:
  base = sys.argv[1]
else:
  base = input("Enter the input directory containing DICOM files: ").strip()

if not os.path.isdir(base):
  raise ValueError(f"Invalid directory: {base}")

# ------------ Finding de.id file (same folder as script)-----------
script_dir = os.path.dirname(os.path.abspath(__file__))
deid_path = os.path.join(script_dir, "bash", "deid.custom")

# --------------------- Output root----------------------------------
clean_root=base + '/clean/'

#  ---------------------- Main de.id loop----------------------------
for root, folders, files in os.walk(base):

# skip already processed data
     if root.startswith(clean_root):
       continue
     for file in files:
       fullpath = os.path.abspath(os.path.join(root, file))
       print(fullpath)

# skip non-DICOM files
        if not file.lower().endswith('.dcm'):
          continue

# mirror folder structure
        try:
          relative_path = os.path.relpath(root, base)
          clean_folder = os.path.join(clean_root, relative_path)
          os.makedirs(clean_folder, exist_ok=True)

          # create cleaner
          clientcustom = DicomCleaner(
          output_folder=clean_folder,
          deid=deid_path
              )

# read DICOM
          ds = pydicom.dcmread(fullpath)

# handle RGB images
            if getattr(ds, 'PhotometricInterpretation', '') == 'RGB':
              print("RGB detected, converting to grayscale before cleaning...")
                gray = (
                    0.299*ds.pixel_array[...,0]
                    + 0.587*ds.pixel_array[...,1]
                    + 0.114*ds.pixel_array[...,2]
                ).astype(ds.pixel_array.dtype)
                ds.PixelData = gray.tobytes()
                ds.PhotometricInterpretation = 'MONOCHROME2'
                ds.SamplesPerPixel = 1

# overwrites original
                ds.save_as(fullpath)

# run cleaning
            result = clientcustom.detect(fullpath)
            print(result)

            clientcustom.clean()
            clientcustom.save_dicom()
            print('done custom clean')

        except Exception as e:
            print("Error:", e)
            continue
print('all done now')
