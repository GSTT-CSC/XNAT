import xnat
import logging
import time


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
                for scan in experiment.scans.values():
                    logging.info(f'\t\tExporting scan to destination: {scan.uri}')
                    try:
                        if 'ORIGINAL' in scan.read_dicom()[0x0008, 0x0008].value:
                            response = session.put('/xapi/dqr/export/', query={'pacsId': pacs['id'], 'session': experiment.id, 'scansToExport': scan.id})
                            logging.debug(response)
                            time.sleep(delay)
                        else:
                            logging.info('\t\tskipping, image not type: ORIGINAL')
                    except ValueError as e:
                        logging.info(f'\t\tskipping, image not dicom: {e}')
                        continue



if __name__ == '__main__':

    xnat_configuration = {'server': 'http://localhost:80',
                          'user': 'admin',
                          'password': 'admin',
                          'project': 'ScaphoidFractures',
                          'verify': 'false'}

    destination = 'horos'
    delay = 10

    send_to_pacs(xnat_configuration, destination, delay=delay)
