import configparser
import json
import logging
import os
import sys
import tempfile
from pathlib import Path
import xnat
from monai.apps import download_and_extract


def upload_nifti_dataset_xnat(config_path, data_root_dir):
    """
    Main function, creates xnat session and sends all subjects to destination
    :param original_data:
    :param xnat_configuration: dictionary with keys 'server', 'user', 'password', 'project', 'verify'
    :return:
    """

    config = configparser.ConfigParser()
    config.read(config_path)

    xnat_configuration = {'server': config['xnat']['SERVER'],
                          'user': config['xnat']['USER'],
                          'password': config['xnat']['PASSWORD'],
                          'project': config['xnat']['PROJECT'],
                          'verify': False}

    data_json_path = os.path.join(data_root_dir, 'dataset.json')

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


def download_data(resource, name):
    directory = os.environ.get("MONAI_DATA_DIRECTORY")
    root_dir = tempfile.mkdtemp() if directory is None else directory
    print(root_dir)

    compressed_file = os.path.join(root_dir, f"{name}.tar")
    data_dir = os.path.join(root_dir, name)
    if not os.path.exists(data_dir):
        download_and_extract(resource, compressed_file, root_dir)
    return data_dir


if __name__ == '__main__':
    """
    usage:

    python create_xnat_data.py <path to config file>

    """

    config_path = sys.argv[1]

    data_dir = download_data(resource="https://msd-for-monai.s3-us-west-2.amazonaws.com/Task04_Hippocampus.tar",
                             name='Task04_Hippocampus',
                             )

    print(f'Data downloaded - uploading to XNAT using config at {config_path}')
    upload_nifti_dataset_xnat(config_path, data_dir)
