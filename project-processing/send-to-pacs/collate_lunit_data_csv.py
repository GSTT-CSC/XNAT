import configparser
import json
import logging
from pathlib import Path

import pandas as pd
import xnat
import os

logging.basicConfig(level=logging.INFO)


def extract_header_info(xnat_configuration: dict, original_data:pd.DataFrame = None, results_data:pd.DataFrame = None,):
    """
    Main function, creates xnat session and sends all subjects to destination
    :param original_data:
    :param xnat_configuration: dictionary with keys 'server', 'user', 'password', 'project', 'verify'
    :return:
    """

    with xnat.connect(server=xnat_configuration['server'],
                      user=xnat_configuration['user'],
                      password=xnat_configuration['password'],
                      verify=xnat_configuration['verify'],
                      ) as session:

        #  get list of XNAT PACS destinations
        logging.info(f'Opened XNAT Session: {session}')
        project = session.projects[xnat_configuration["project"]]

        results_list = []
        for subject in project.subjects.values():
            logging.info(f'Subject: {subject}')
            for experiment in subject.experiments.values():
                logging.info(f'\tExperiment: {experiment}')

                try:
                    df2 = get_lunit_header_csv(experiment, subject, results_data)

                except MultipleOriginalImages:
                    logging.warning(f'Subject {subject} has no valid dicom resource!')
                    results_list.append(pd.DataFrame({'Subject': [subject.label],
                                                      'EXCLUDE': [True],
                                                      'EXCLUSION_REASON': MultipleOriginalImages.__name__}).set_index('Subject'))
                    continue

                except ValueError:
                    logging.warning(f'Subject {subject} has no valid dicom resource!')
                    results_list.append(pd.DataFrame({'Subject': [subject.label],
                                                      'EXCLUDE': [True],
                                                      'EXCLUSION_REASON': NoValidDicomResource.__name__}).set_index('Subject'))
                    continue

                if df2.empty:
                    logging.info(f'Subject {subject} has no findings')
                    continue
                else:
                    results_list.append(df2)

    df = pd.concat(results_list)
    #  reorder to have exclusion and reason at start
    cols = list(df.columns.values)
    cols.pop(cols.index('EXCLUDE'))
    cols.pop(cols.index('EXCLUSION_REASON'))
    df = df[['EXCLUDE', 'EXCLUSION_REASON'] + cols]

    out = pd.concat([original_data.set_index('Subject'), df], axis=1).fillna(0)

    return out

def get_lunit_header_csv(experiment, subject, results_data):
    #  if multiple images in dataset, exclude
    if len([x for x in [scan.id for scan in experiment.scans.values()] if 'ORIGINAL' in experiment.scans[x].dicom_dump(fields='00080008')[0]['value']]) > 1:
        logging.info(f'\t\tExcluding due to multiple ORIGINAL images in {experiment}')
        raise MultipleOriginalImages

    lunit_results = [x for x in [scan.id for scan in experiment.scans.values()] if
                     'Lunit' in experiment.scans[x].dicom_dump(fields='00080070')[0]['value']]
    logging.info(f'found lunit results: {lunit_results}')

    # for now just take the newest lunit result
    lunit_results.sort()
    result = lunit_results[-1]

    lunit_header = experiment.scans[result].read_dicom(read_pixel_data=False)
    study_uid = lunit_header[0x0020, 0x000D].value

    rslt_df = results_data[results_data['study_instance_uid'] == study_uid]

    most_recent = rslt_df.iloc[-1]

    df2 = most_recent.to_frame().transpose().set_index('patient_id')

    return df2


def get_lunit_header(experiment, subject):
    #  if multiple images in dataset, exclude
    if len([x for x in [scan.id for scan in experiment.scans.values()] if 'ORIGINAL' in experiment.scans[x].dicom_dump(fields='00080008')[0]['value']]) > 1:
        logging.info(f'\t\tExcluding due to multiple ORIGINAL images in {experiment}')
        raise MultipleOriginalImages

    lunit_results = [x for x in [scan.id for scan in experiment.scans.values()] if
                     'Lunit' in experiment.scans[x].dicom_dump(fields='00080070')[0]['value']]
    logging.info(f'found lunit results: {lunit_results}')

    # for now just take the newest lunit result
    lunit_results.sort()
    result = lunit_results[-1]

    lunit_header = experiment.scans[result].read_dicom(read_pixel_data=False)
    r = lunit_header[0x0009, 0x1003].value[0][0x0009, 0x1004].value
    k = json.loads(r)

    # get maximum value in cases where multiple regions identified
    result_df = pd.DataFrame(k['Findings'])
    result_df.sort_values(by=['AbnormalityScore'], inplace=True)
    result_df['Name'] = 'LUNIT_' + result_df['Name'].astype(str)
    result_df.drop_duplicates(subset='Name', keep='last', inplace=True)
    logging.info(f'results df: {result_df}')
    series = result_df.set_index('Name').iloc[:, 0]
    series['Subject'] = subject.label
    logging.info(f'Storing results: {series}')
    df2 = series.to_frame().transpose().set_index('Subject')

    return df2


class MultipleOriginalImages(Exception):
    """Multiple original images present"""


class NoValidDicomResource(ValueError):
    """No valid dicom resource could be found"""


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.cfg')

    original_data_path = Path(config['data']['path'])
    original_data = pd.read_csv(original_data_path)

    results_data_path = Path(config['data']['results_path'])
    results_data = pd.read_csv(results_data_path,  delimiter='|')
    results_data = results_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    results_data = results_data.rename(columns=lambda x: x.strip())

    xnat_configuration = {'server': config['xnat']['SERVER'],
                          'user': config['xnat']['USER'],
                          'password': config['xnat']['PASSWORD'],
                          'project': config['xnat']['PROJECT'],
                          'verify': False}

    destination = config['xnat']['DESTINATION']
    delay = int(config['xnat']['DELAY'])

    out = extract_header_info(xnat_configuration=xnat_configuration, original_data=original_data, results_data=results_data)
    out_path = os.path.join(str(original_data_path.parent), original_data_path.stem + '_result' + original_data_path.suffix)
    logging.info(f'Writing results to: {out_path}')
    out.to_csv(out_path)