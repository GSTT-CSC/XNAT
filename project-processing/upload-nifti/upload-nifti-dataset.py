import logging
import xnat
import configparser
import os
import json
from pathlib import Path


logging.basicConfig(level=logging.INFO)


def upload_nifti_dataset(data, xnat_configuration, data_root_dir):
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
        xnat_objs = dir(session.classes)

        for subject, data_i in enumerate(data['training']):

            subject = str(subject)

            # if Subject does not create new experiment
            if subject in project.subjects:
                xnat_subject = project.subjects[subject]
            else:
                xnat_subject = session.classes.SubjectData(parent=project, label=subject)

            # if experiment does not create new experiment
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
                    xnat_scan = session.classes.MrScanData(parent=xnat_experiment, id=scan, type=scan, series_description=im_type, label=scan)

                # If resource exists create new resource
                res = f'{scan}_resource'
                if res in xnat_scan.resources:
                    xnat_resource = xnat_scan.resources[res]
                else:
                    xnat_resource = session.classes.ResourceCatalog(parent=xnat_scan, label=res)

                file_ = Path(os.path.join(data_root_dir, data_i[im_type]))
                xnat_resource.upload(str(file_), file_.name)
                print(f'uploaded {file_}')


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.cfg')

    xnat_configuration = {'server': config['xnat']['SERVER'],
                          'user': config['xnat']['USER'],
                          'password': config['xnat']['PASSWORD'],
                          'project': config['xnat']['PROJECT'],
                          'verify': False}

    data_root_dir = '/Users/lj16/Downloads/Task04_Hippocampus'
    data_json_path = os.path.join(data_root_dir, 'dataset.json')
    with open(data_json_path) as data_file:
        data = data_file.read()
        data_content = json.loads(data)

    upload_nifti_dataset(data_content, xnat_configuration, data_root_dir)
