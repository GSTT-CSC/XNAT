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
            if int(subject.label) > 705:  # filter to avoid data that has already been sent
                for experiment in subject.experiments.values():
                    logging.info(f'\tExperiment: {experiment}')
                    send_lunit_data(session, experiment, pacs)


def send_lunit_data(session, experiment, pacs):
    # check if any series called '99999999' is already in session
    # if any('99999999' in x for x in [scan.id for scan in experiment.scans.values()]):
    #     logging.info(f'\t\tLunit data already available in {experiment}')
    #     pass
    # elif len([x for x in [scan.id for scan in experiment.scans.values()] if 'ORIGINAL' in experiment.scans[x].dicom_dump(fields='00080008')[0]['value']]) > 1:
    #     logging.info(f'\t\tExcluding due to multiple ORIGINAL images in {experiment}')
    # else:
    for scan in experiment.scans.values():
        logging.info(f'\t\tExporting scan to destination: {scan.uri}')
        attempt = 0
        n_attempts = 5
        while attempt < n_attempts:
            try:
                query = {'pacsId': pacs['id'], 'session': experiment.id, 'scansToExport': scan.id}
                response = session.put('/xapi/dqr/export/', query=query)
                logging.debug(response)
                logging.debug(query)

                break

            except Exception as e:
                logging.info(f'Send failed - attempt {attempt}')
                attempt += 1
                time.sleep(delay)
                if attempt == n_attempts:
                    raise Exception(f'Image loader failed on {scan} : {session} after 3 retries due to {e}')

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
