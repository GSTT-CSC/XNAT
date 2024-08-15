"""
Extracts metadata from XNAT projects' backend folders.

Usage:
    python3 SeriesDescription_Extractor.py PROJECT_FOLDER_PATH OUTPUT_FILE_PATH

"""

# import pandas as pd
from pathlib import Path
import pydicom
import sys

root_directory = Path(sys.argv[1])
output_filepath = Path(sys.argv[2])


def contains_dicom_files(directory):
    for dcm_file in directory.glob('*.dcm'):
        return True
    return False


def process_directory(directory):
    session_name = directory.parent.parent.name
    series_description = None
    dicom_found = False

    # Find the first .dcm file in the directory
    for dcm_file in directory.glob('*.dcm'):
        ds = pydicom.dcmread(dcm_file)
        series_description = ds.SeriesDescription
        dicom_found = True
        break

    # Traverse upward to find the top-level "Data" folder
    parent = directory
    while parent.name != "data":
        parent = parent.parent

    series_name = directory.parent.name

    # Create a DataFrame row for the folder
    if dicom_found:
        return {'Session': session_name,
                'Series': series_name,
                'SeriesDescription': series_description}
    else:
        return {'Session': session_name,
                'Series': series_name,
                'SeriesDescription': 'NO DICOMS'}


# Initialize an empty DataFrame
# df = pd.DataFrame(columns=['Session', 'Series', 'SeriesDescription'])
columns = ['Session', 'Series', 'SeriesDescription']

f = open(output_filepath, "w")
f.writelines("%s\n" % columns)

# Recursively process each directory, starting from the deepest level
for directory in sorted(root_directory.rglob('*'), key=lambda x: len(x.parts), reverse=True):
    if directory.is_dir() and contains_dicom_files(directory):
        row = process_directory(directory)
        values = [value for value in row.values()]
        comma_delimited_string = ', '.join(values)
        f.writelines("%s\n" % comma_delimited_string)
        # print(row)
        # row_df = pd.DataFrame(row, index=[0])
        # df = pd.concat([df, row_df])

# Write df to csv
# filepath = Path(output_filepath)
# filepath.parent.mkdir(parents=True, exist_ok=True)
# df.to_csv(filepath)
