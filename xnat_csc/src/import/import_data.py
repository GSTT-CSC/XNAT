import configparser
import json
import logging
import os
import sys
import tempfile
from pathlib import Path
import xnat
import time
import zipfile as zf

logging.basicConfig(level=logging.INFO)


def unzip(zipdirectorypath, destdirectorypath):
    with zf.ZipFile(zipdirectorypath, 'r') as zipdirectory:
        zipdirectory.extractall(destdirectorypath)


def import(configpath, directorypath):
    config = configparser.ConfigParser()
    config.read(configpath)

    xnat_configuration = {'server': config['xnat']['SERVER'],
                          'user': config['xnat']['USER'],
                          'password': config['xnat']['PASSWORD'],
                          'project': config['xnat']['PROJECT'],
                          'verify': False}

    data_json_path = os.path.join(directorypath, 'dataset.json')

    with open(data_json_path) as data_file:
        data = data_file.read()
        data_content = json.loads(data)

    with xnat.connect(server=xnat_configuration['server'],
                      user=xnat_configuration['user'],
                      password=xnat_configuration['password'],
                      verify=xnat_configuration['verify'],
                      ) as session:

        #  get list of XNAT PACS destinations
        logging.info(f'Opened XNAT Session: {session}')
        project = session.projects[xnat_configuration["project"]]

        for subject, data_i in enumerate(data_content['training']):

            subject = str(subject).zfill(4)

            # if Subject does not create new experiment
            if subject in project.subjects:
                xnat_subject = project.subjects[subject]
            else:
                xnat_subject = session.classes.SubjectData(parent=project, label=subject)
                xnat_subject.fields['test_api'] = 'didthiswork'
                # curl request for adding fields - e.g. 'handedness'='r'
                # curl -X PUT "http://localhost:80/REST/projects/hipposeg2/subjects/0000/" --data "xnat:subjectData/fields/field[name%3Dhandedness]/field=r" -u admin:admin

            #  if experiment does not create new experiment
            experiment = f'{subject}_exp'
            if experiment in xnat_subject.experiments:
                xnat_experiment = xnat_subject.experiments[experiment]
            else:
                xnat_experiment = session.classes.MrSessionData(parent=xnat_subject, label=experiment)

            for im_type in ['image', 'label']:
                # if scan does not exist create new Scan
                scan = f'{experiment}_{im_type}'
                if scan in xnat_experiment.scans:
                    xnat_scan = xnat_experiment.scans[scan]
                else:
                    xnat_scan = session.classes.MrScanData(parent=xnat_experiment, id=scan, type=scan,
                                                           series_description=im_type, label=scan)

                # If resource exists create new resource
                res = f'{scan}_resource'
                if res in xnat_scan.resources:
                    xnat_resource = xnat_scan.resources[res]
                else:
                    xnat_resource = session.classes.ResourceCatalog(parent=xnat_scan, label=res)

                file_ = Path(os.path.join(data_root_dir, data_i[im_type]))
                xnat_resource.upload(str(file_), file_.name)
                print(f'uploaded {file_}')


def send_to_pacs(xnat_configuration: dict, destination: str, delay: int = 10):
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
        pacs_list = session.get_json('/xapi/pacs/')
        pacs = [x for x in pacs_list if x['label'] == destination][0]
        project = session.projects[xnat_configuration["project"]]

        logging.info(f'Sending data in project {project} to PACS destination: {pacs}')
        for subject in project.subjects.values():
            logging.info(f'Subject: {subject}')
            for experiment in subject.experiments.values():
                logging.info(f'\tExperiment: {experiment}')
                for scan in experiment.scans.values():
                    logging.info(f'\t\tExporting scan to destination: {scan.uri}')
                    response = session.put('/xapi/dqr/export/', query={'pacsId': pacs['id'], 'session': experiment.id,
                                                                       'scansToExport': scan.id})
                    logging.debug(response)
                    time.sleep(delay)


if __name__ == '__main__':
    xnat_configuration = {'server': 'http://localhost:80',
                          'user': 'admin',
                          'password': 'admin',
                          'project': 'ScaphoidFractures',
                          'verify': 'false'}

    destination = 'horos'
    delay = 10

    send_to_pacs(xnat_configuration, destination, delay=delay)
