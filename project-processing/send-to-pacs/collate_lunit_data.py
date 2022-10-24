import xnat
import logging
import time
import configparser
import pandas
import json
from pathlib import Path, PurePath

logging.basicConfig(level=logging.INFO)


def extract_header_info(xnat_configuration: dict, destination: str, original_data=None, delay: int = 10):
    """
    Main function, creates xnat session and sends all subjects to destination
    :param destination: name of PACS destination (label in xnat)
    :param xnat_configuration: dictionary with keys 'server', 'user', 'password', 'project', 'verify'
    :param delay: additional delay in seconds after each scan is sent
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
                result_df = pandas.DataFrame(findings)
                result_df['Name'] = 'LUNIT_' + result_df['Name'].astype(str)
                series = result_df.set_index('Name').squeeze()
                series['Subject'] = subject.label
                df2 = series.to_frame().transpose()
                original_data = pandas.merge(original_data, df2, on='Subject', how='outer')

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

    original_data_path = PurePath('/Users/lj16/code/DATA/lunit/test_set/Test 20 dataset 4.8.22.csv')

    original_data = pandas.read_csv(original_data_path)

    xnat_configuration = {'server': config['xnat']['SERVER'],
                          'user': config['xnat']['USER'],
                          'password': config['xnat']['PASSWORD'],
                          'project': config['xnat']['PROJECT'],
                          'verify': False}

    destination = config['xnat']['DESTINATION']
    delay = int(config['xnat']['DELAY'])

    out = extract_header_info(xnat_configuration, destination, original_data, delay=delay)

    out.to_csv(original_data_path.with_stem(original_data_path.stem + '_result'))
