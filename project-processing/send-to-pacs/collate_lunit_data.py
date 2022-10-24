import configparser
import json
import logging
from pathlib import PurePath

import pandas as pd
import xnat

logging.basicConfig(level=logging.INFO)


def extract_header_info(xnat_configuration: dict, original_data:pd.DataFrame = None):
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

        for subject in project.subjects.values():
            logging.info(f'Subject: {subject}')
            for experiment in subject.experiments.values():
                logging.info(f'\tExperiment: {experiment}')
                findings = get_lunit_header(experiment)
                result_df = pd.DataFrame(findings)
                result_df['Name'] = 'LUNIT_' + result_df['Name'].astype(str)
                series = result_df.set_index('Name').squeeze()
                series['Subject'] = subject.label
                df2 = series.to_frame().transpose()
                original_data = pd.merge(original_data, df2, on='Subject', how='outer')

        return original_data


def get_lunit_header(experiment):
    lunit_results = [x for x in [scan.id for scan in experiment.scans.values()] if
                     'Lunit' in experiment.scans[x].dicom_dump(fields='00080070')[0]['value']]

    # for now just take the newest lunit result
    lunit_results.sort()
    result = lunit_results[-1]

    lunit_header = experiment.scans[result].read_dicom(read_pixel_data=False)
    r = lunit_header[0x0009, 0x1003].value[0][0x0009, 0x1004].value
    k = json.loads(r)
    return k['Findings']


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.cfg')

    original_data_path = PurePath(config['data']['path'])
    original_data = pd.read_csv(original_data_path)

    xnat_configuration = {'server': config['xnat']['SERVER'],
                          'user': config['xnat']['USER'],
                          'password': config['xnat']['PASSWORD'],
                          'project': config['xnat']['PROJECT'],
                          'verify': False}

    destination = config['xnat']['DESTINATION']
    delay = int(config['xnat']['DELAY'])

    out = extract_header_info(xnat_configuration, destination, original_data, delay=delay)
    out_path = original_data_path.with_stem(original_data_path.stem + '_result')
    logging.info(f'Writing results to: {out_path}')
    out.to_csv(out_path)
