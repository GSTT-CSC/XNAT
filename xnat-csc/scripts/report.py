"""
Creates reports on successful/failed ingestion and accession number traces.

Usage:

python report.py <DIRECTORY_PATH> accession-trace <STUDY_DESCRIPTION> <DATE_FLAG> <OUTPUT_FILENAME>
python report.py <DIRECTORY_PATH> ingestion-status <OUTPUT_FILENAME>

"""""
import pathlib as p
import warnings
import pandas as pd
import argparse
import json
import numpy as np

warnings.filterwarnings("ignore")


def parse_arguments():
    parser = argparse.ArgumentParser(description='Define task before task-specific required details')
    parser.add_argument('dir_path', metavar='Directory', type=str, action="store",
                        help='Directory to perform task')
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    # Subparser for accession-trace
    parse_at = subparsers.add_parser('accession-trace')
    parse_at.add_argument('study_description', metavar='Study description', type=str, action="store",
                          help='Study description to filter on. If you would like to see all, enter "All"')
    parse_at.add_argument('date_flag', metavar='Study date flag', type=int, action="store",
                          help='Flag to include study date in trace, e.g. 1 to include, 0 to ignore')
    parse_at.add_argument('filename', metavar='Output filename', type=str, action="store", help='Output filename')

    # Subparser for swagger-report
    parser_sr = subparsers.add_parser('ingestion-status')
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
    # Relative directory path
    directory = p.Path(__file__).parent

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

    # Export report CSV to user home folder
    # report_df.to_csv(pathlib.Path.home() / 'home' / f'{username}' / f'{reportname}.csv', index=False)
    # Export report CSV
    report_df.to_csv(directory / f'{reportname}.csv', index=False)


def subject_master_list(dirpath, studydescription, studydateflag, reportname):
    """
    Maps accession ID trace request and results into a consolidated subject master list
    :param dirpath: Path to directory containing CSV file(s) submitted via Swagger and JSON response(s)
    :param studydescription: Study description of interest, i.e. keep only specific JSON response records
    :param studydateflag: Flag to include study date in trace
    :param reportname: Filename of the output file
    """
    # Relative directory path
    directory = p.Path(__file__).parent

    csv_df = pd.DataFrame()
    json_df = pd.DataFrame()

    # Iterate through files in directory
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
            for colname, colval in studies_df.iteritems():
                temp_df = pd.DataFrame(colval.values)[0].apply(pd.Series).rename(columns={
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
                json_df = json_df.append(temp_df, ignore_index=True)
            if studydescription != 'All':
                json_df = json_df.loc[json_df['StudyDescription'].str.casefold() == studydescription.casefold()]
            else:
                pass
        elif file.suffix == '.csv':
            data = pd.read_csv(file)
            csv_df = csv_df.append(data, ignore_index=True)
    csv_df.rename(columns={'Patient ID': 'PatientID', 'Study Date': 'StudyDate'}, inplace=True)
    csv_df['StudyDate'] = pd.to_datetime(csv_df['StudyDate'].astype(str), format='%Y%m%d')
    # csv_df['StudyDate'] = pd.to_datetime(csv_df['StudyDate'], dayfirst=True)
    json_df = json_df[['PatientID', 'AccessionNumber', 'StudyDate', 'StudyID', 'StudyInstanceUID', 'StudyDescription']]
    json_df['StudyDate'] = pd.to_datetime(json_df['StudyDate'], dayfirst=True)
    if studydateflag == 1:
        final_df = pd.merge(csv_df, json_df, how='outer', left_on=['PatientID', 'StudyDate'], right_on=['PatientID',
                                                                                                        'StudyDate'])
    else:
        final_df = pd.merge(csv_df, json_df, how='outer', left_on=['PatientID'], right_on=['PatientID'])

    # Export report CSV to user home folder
    # report_df.to_csv(pathlib.Path.home() / 'home' / f'{username}' / f'{reportname}.csv', index=False)
    # Export report CSV
    final_df.to_csv(directory / f'{reportname}.csv', index=False)


if __name__ == "__main__":
    arguments = parse_arguments()
    if arguments.subcommand == "accession-trace":
        print("\nCreating subject master list with traced accession numbers...\n")
        subject_master_list(p.Path(arguments.dir_path), arguments.study_description, arguments.date_flag,
                            arguments.filename)
    elif arguments.subcommand == "swagger-report":
        print("\nCreating ingestion status report...\n")
        swagger_report(arguments.failure_json, arguments.success_csv, arguments.filename)
    else:
        print("\nNo task to be performed.\n")
