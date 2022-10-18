"""
Creates report of successfully-ingested and problematic accession IDs

Usage:

"""""
import pathlib
import warnings
import pandas as pd
import argparse
import json
import numpy as np

warnings.filterwarnings("ignore")


def parse_arguments():
    parser = argparse.ArgumentParser(description='Returns report on successfully and unsuccessfully-ingested accession '
                                                 'IDs.')
    parser.add_argument('failure_json', metavar='JSON filepath', type=str, action="store",
                        help='Path to JSON response from Swagger UI in XNAT containing unsuccessfully-ingested '
                             'accession IDs')
    parser.add_argument('success_csv', metavar='CSV filepath', type=str, action="store",
                        help='Path to CSV downloaded from from Subject > Options > Spreadsheet in the Project page in '
                             'XNAT containing successfully-ingested accession IDs')
    parser.add_argument('username', metavar='username', type=str, action="store",
                        help='Username')
    parser.add_argument('report_name', metavar='Output filename', type=str, action="store",
                        help='Output filename')
    arguments = parser.parse_args()
    return arguments


# TODO: Add connect() for XNAT API (see https://gitlab.com/KCL-BMEIS/Data-Analytics/DaDa/-/wikis/The-XNAT-REST-API)

def report(swaggerresponse, spreadsheet, username, reportname):
    """
    Categorises success/failure statuses of original accession IDs ingestion
    :param swaggerresponse: Path to JSON containing response from Swagger UI
    :param spreadsheet: Path to CSV containing subjects which were successfully-ingested in XNAT (downloaded from
    Subject > Options in Project page)
    :param username: Username
    :param reportname: Filename of the output file
    """

    # Read CSV containing successfully-ingested accession IDs and assign "Success" status
    success_df = pd.read_csv(spreadsheet)
    success_df['Status'] = 'Success'

    # Read JSON containing unsuccessfully-ingested accession IDs
    with open(swaggerresponse) as json_file:
        data = json.load(json_file)

    df = pd.json_normalize(data).rename(columns={
        'criteria.accessionNumber': 'AccessionNumber',
        'criteria.pacsId': 'PACSID',
        'criteria.seriesNumber': 'SeriesNumber',
        'relabelMap.Subject': 'Subject',
        'relabelMap.Session': 'Session',
    })

    studies_df = pd.json_normalize(df['studies'])
    # Get values into separate columns
    new_studies_df = studies_df[0].apply(pd.Series).rename(columns={
        'studyId': 'StudyID',
        'studyDescription': 'StudyDescription',
        'accessionNumber': 'AccessionNumber',
        'studyDate': 'StudyDate',
        'referringPhysicianName': 'ReferringPhysicianName',
        'patient.id': 'PatientID',
        'patient.name': 'PatientName',
        'patient.sex': 'PatientSex',
        'studyInstanceUid': 'StudyInstanceUID',
        'modalitiesInStudy': 'ModalitiesInStudy'
    })

    # Keep only columns needed for status assignment
    new_studies_df = new_studies_df[['StudyID', 'StudyInstanceUID', 'AccessionNumber']]
    df = df[['AccessionNumber', 'Subject', 'Session']]
    failure_df = df.merge(new_studies_df, on='AccessionNumber', how='left')

    # Failure status conditions
    conditions = [
        (failure_df['StudyID'].isna()),
        (failure_df['StudyID'].notna() & failure_df['StudyInstanceUID'].isna()),
        (failure_df['StudyID'].notna() & failure_df['StudyInstanceUID'].notna()),
    ]

    # Failure status values per condition, i.e. to assist with investigation
    values = [
        'Accession number is wrong or is not attached to any images',
        'No study instance UID attached to accession number, i.e. no images found',
        'Should have been successfully ingested'
    ]

    # Assign relevant status value based on conditions
    failure_df['Status'] = np.select(conditions, values)
    # Merge successfully and unsuccessfully-ingested accession IDs
    report_df = pd.concat([success_df, failure_df], axis=0, ignore_index=True)
    # Replace all Nan values to empty string for better readability
    report_df.fillna('', inplace=True)

    # Relative directory path
    directory = pathlib.Path(__file__).parent

    # Export report CSV to user home folder
    # report_df.to_csv(pathlib.Path.home() / 'home' / f'{username}' / f'{reportname}.csv', index=False)
    # Export report CSV
    report_df.to_csv(directory / f'{reportname}.csv', index=False)


if __name__ == "__main__":
    args = parse_arguments()
    user_folder = args.username
    response_json = args.failure_json
    spreadsheet_csv = args.success_csv
    report_name = args.report_name
    report(response_json, spreadsheet_csv, user_folder, report_name)
