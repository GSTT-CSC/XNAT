import xnat
import logging
import time
import configparser


logging.basicConfig(level=logging.INFO)


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
                if any('Lunit' in x for x in [x.read_dicom()[0x0008, 0x0070].value for x in experiment.scans.values()]):
                    logging.info(f'\t\tLunit data already available in {experiment}')
                    continue
                for scan in experiment.scans.values():
                    logging.info(f'\t\tExporting scan to destination: {scan.uri}')
                    try:
                        if 'Lunit' not in scan.read_dicom()[0x0008, 0x0070].value:
                            response = session.put('/xapi/dqr/export/', query={'pacsId': pacs['id'], 'session': experiment.id, 'scansToExport': scan.id})
                            logging.debug(response)
                        else:
                            logging.info(f'\t\tskipping, "Lunit" in manufacturer {scan.read_dicom()[0x0008, 0x0008].value}')
                    except Exception as e:
                        logging.exception(f'\t\tException: {e}')
                        continue
                    time.sleep(delay)


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('config.cfg')

    xnat_configuration = {'server': config['xnat']['SERVER'],
                          'user': config['xnat']['USER'],
                          'password': config['xnat']['PASSWORD'],
                          'project': config['xnat']['PROJECT'],
                          'verify': False}

    destination = config['xnat']['DESTINATION']
    delay = int(config['xnat']['DELAY'])

    send_to_pacs(xnat_configuration, destination, delay=delay)
