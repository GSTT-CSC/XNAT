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
                send_lunit_data(session, experiment, pacs)


def send_lunit_data(session, experiment, pacs):
    check if any series called '99999999' is already in session
    if any('99999999' in x for x in [scan.id for scan in experiment.scans.values()]):
        logging.info(f'\t\tLunit data already available in {experiment}')
        pass
    elif len([x for x in [scan.id for scan in experiment.scans.values()] if 'ORIGINAL' in experiment.scans[x].dicom_dump(fields='00080008')[0]['value']]) > 1:
        logging.info(f'\t\tExcluding due to multiple ORIGINAL images in {experiment}')
    else:
        for scan_i in experiment.scans:
            scan = experiment.scans[scan_i]
            if scan.modality not in ['CR', 'DX']:
                logging.info(f'Data {scan} not type CR or DX')
            else:
                # n_attempts = 3
                # attempt = 0
                # while attempt <= n_attempts:
                #     try:
                #         logging.info(f'\t\tExporting scan to destination: {scan.uri} - attempt {attempt}')
                #         response = session.put('/xapi/dqr/export/',
                #                                query={'pacsId': pacs['id'], 'session': experiment.id, 'scansToExport': scan.id})
                #         logging.debug(response)
                #         time.sleep(delay)
                #         break
                #     except Exception as e:
                #         attempt = attempt + 1
                #         time.sleep(delay)
                #         if attempt == n_attempts:
                #             logging.info(f'\t\tFAILED : {scan.uri}')
                #             with open("failed_sends.txt", "a") as myfile:
                #                 myfile.write(scan.uri)
                #         else:
                #             continue
                #     break
                for attempt in range(3):
                    try:
                        logging.info(f'\t\tExporting scan to destination: {scan.uri} - attempt {attempt}')
                        response = session.put('/xapi/dqr/export/',
                                           query={'pacsId': pacs['id'], 'session': experiment.id, 'scansToExport': scan.id})
                        logging.debug(response)
                        time.sleep(delay)
                    except Exception as e:
                        logging.info(f'\t\tFAILED RETRYING: {scan.uri} exception: {e}')
                        time.sleep(delay)
                    else:
                        break
                else:
                    logging.info(f'\t\tFAILED all attempts - moving on {scan.uri}')
                    with open("failed_sends.txt", "a") as myfile:
                        myfile.write(scan.uri + "\n")


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
