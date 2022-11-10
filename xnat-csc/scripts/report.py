"""
Creates reports on successful/failed ingestion and accession number traces.

Usage:

"""""
import pathlib as p
import warnings
import pandas as pd
import argparse
import json
import numpy as np

warnings.filterwarnings("ignore")


def parse_arguments():
    parser = argparse.ArgumentParser(description='Define job type before job-specific required details')
    parser.add_argument('dir_path', metavar='Directory', type=str, action="store",
                        help='Directory to perform task')
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    # Subparser for accession-trace
    parse_at = subparsers.add_parser('accession-trace')
    # parse_at.add_argument('username', metavar='username', type=str, action="store", help='Username')
    parse_at.add_argument('study_description', metavar='Study description', type=str, action="store",
                          help='Study description to filter on. If you would like to see all, enter "All" ')
    parse_at.add_argument('filename', metavar='Output filename', type=str, action="store", help='Output filename')

    # Subparser for swagger-report
    parser_sr = subparsers.add_parser('ingestion-status')
    # parser_sr.add_argument('failure_json', metavar='JSON filepath', type=str, action="store",
    #                        help='Path to JSON response from Swagger UI in XNAT containing unsuccessfully-ingested'
    #                             ' accession IDs')
    # parser_sr.add_argument('success_csv', metavar='CSV filepath', type=str, action="store",
    #                        help='Path to CSV downloaded from from Subject > Options > Spreadsheet in the Project page'
    #                             ' in XNAT containing successfully-ingested accession IDs')
    # parser_sr.add_argument('username', metavar='username', type=str, action="store", help='Username')
    parser_sr.add_argument('filename', metavar='Output filename', type=str, action="store", help='Output filename')

    args = parser.parse_args()
    return args


# TODO: Add connect() for XNAT API (see https://gitlab.com/KCL-BMEIS/Data-Analytics/DaDa/-/wikis/The-XNAT-REST-API)
# TODO: Add pathlib() to use username arg for filepath
def swagger_report(swaggerresponse, spreadsheet, reportname):
    """
    Categorises success/failure statuses of original accession IDs ingestion
    :param swaggerresponse: Path to JSON containing response from Swagger UI
    :param spreadsheet: Path to CSV containing subjects which were successfully-ingested in XNAT (downloaded from
    Subject > Options in Project page)
    # :param username: Username
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
    directory = p.Path(__file__).parent

    # Export report CSV to user home folder
    # report_df.to_csv(pathlib.Path.home() / 'home' / f'{username}' / f'{reportname}.csv', index=False)
    # Export report CSV
    report_df.to_csv(directory / f'{reportname}.csv', index=False)


def subject_master_list(dirpath, studydescription, reportname):
    """
    Maps accession ID trace request and results into a consolidated subject master list
    :param dirpath: Path to directory containing CSV file(s) submitted via Swagger and JSON response(s)
    :param studydescription: Study description of interest, i.e. keep only specific JSON response records
    # :param username: Username
    :param reportname: Filename of the output file
    """

    csv_df = pd.DataFrame()
    json_df = pd.DataFrame()
    print(studydescription)

    # Iterate through JSON files in directory
    for file in p.Path.iterdir(dirpath):
        if file.suffix == '.json':
            with open(file) as json_file:
                data = json.load(json_file)

            df = pd.json_normalize(data).rename(columns={
                'criteria.patientId': 'PatientID',
                'criteria.pacsId': 'PACSID',
                'criteria.seriesNumber': 'SeriesNumber',
                # 'criteria.studyDateRange.start': 'StudyDateRangeStart',
                # 'criteria.studyDateRange.end': 'StudyDateRangeEnd',
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

            new_studies_df = new_studies_df[['PatientID', 'AccessionNumber', 'StudyDate', 'StudyID', 'StudyInstanceUID',
                                             'StudyDescription']]
            if studydescription.casefold() == 'All':
                json_df = json_df.append(new_studies_df, ignore_index=True)
            else:
                new_df = new_studies_df.loc[new_studies_df['StudyDescription'].str.casefold() == studydescription.casefold()]
                json_df = json_df.append(new_df, ignore_index=True)
        elif file.suffix == '.csv':
            data = pd.read_csv(file)
            csv_df = csv_df.append(data, ignore_index=True)
    csv_df.rename(columns={'Patient ID': 'PatientID', 'Study Date': 'StudyDate'}, inplace=True)
    #csv_df['StudyDate'] = pd.to_datetime(csv_df['StudyDate'], dayfirst=True)
    csv_df['StudyDate'] = pd.to_datetime(csv_df['StudyDate'].astype(str), format='%Y%m%d')
    json_df['StudyDate'] = pd.to_datetime(json_df['StudyDate'], dayfirst=True)
    final_df = pd.merge(csv_df, json_df, how='left', left_on=['PatientID', 'StudyDate'], right_on=['PatientID', 'StudyDate'])

    # Relative directory path
    directory = p.Path(__file__).parent
    # Export report CSV to user home folder
    # report_df.to_csv(pathlib.Path.home() / 'home' / f'{username}' / f'{reportname}.csv', index=False)
    # Export report CSV
    final_df.to_csv(directory / f'{reportname}.csv', index=False)


if __name__ == "__main__":
    arguments = parse_arguments()
    if arguments.subcommand == "accession-trace":
        print("\nCreating subject master list with traced accession numbers...\n")
        subject_master_list(p.Path(arguments.dir_path), arguments.study_description, arguments.filename)
    elif arguments.subcommand == "swagger-report":
        print("\nCreating ingestion status report...\n")
        swagger_report(arguments.failure_json, arguments.success_csv, arguments.filename)
    else:
        print("\nNo task to be performed.\n")
