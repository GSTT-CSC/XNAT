import argparse
import re
import os
import xnat
import tqdm
import logging
import time
import yaml

logging.basicConfig(level=logging.INFO)


def send_to_pacs(config):

    with xnat.connect(server=config['xnat']['url'],
                      user=config['xnat']['user'],
                      password=config['xnat']['password'],
                      verify=config['xnat']['verify'] if 'verify' in config['xnat'] else False,
                      loglevel='ERROR',
                      ) as session:

        logging.info(f'Opened XNAT Session: {session}')
        pacs_list = session.get_json('/xapi/pacs/')
        pacs = [x for x in pacs_list if x['label'] == config['destination']['name']][0]

        project = session.projects[config['xnat']['project_id']]

        for subject in project.subjects.values():
            logging.debug(f'Subject: {subject}')
            # Add subject level inclusion/exclusion criteria here
            for experiment in subject.experiments.values():
                logging.debug(f'\tExperiment: {experiment}')
                # Add experiment level inclusion/exclusion criteria here
                for scan in experiment.scans.values():
                    logging.debug(f'\tScan: {experiment}')
                    # Add scan level inclusion/exclusion criteria here
                    for attempt in range(config['settings']['attempts']):
                        try:
                            response = session.put('/xapi/dqr/export/', query={'pacsId': pacs['id'], 'session': experiment.id, 'scansToExport': scan.id})
                            logging.debug(response)
                        except Exception as e:
                            last_e = e
                            logging.warning(f'RETRYING - {attempt+1}; exception: {e}')
                        else:
                            break
                        finally:
                            time.sleep(config['settings']['delay'])
                    else:
                        logging.warning(f"FAILED after {config['settings']['attempts']} attempts: {subject}, {experiment}, {scan}; exception: {last_e}")
                        if 'failure_log' in config['settings']:
                            with open(config['settings']['failure_log'], "a") as f:
                                f.write(f"{subject},{experiment},{scan},{last_e}\n")


def parse_config_yml(yml_path):
    path_matcher = re.compile(r'\$\{([^}^{]+)}')

    def path_constructor(loader, node):
        """ Extract the matched value, expand env variable, and replace the match """
        value = node.value
        match = path_matcher.match(value)
        env_var = match.group()[2:-1]
        return os.environ.get(env_var) + value[match.end():]

    yaml.add_implicit_resolver('!path', path_matcher, None, yaml.SafeLoader)
    yaml.add_constructor('!path', path_constructor, yaml.SafeLoader)

    with open(yml_path, "r") as stream:
        try:
            conf = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return conf


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Send XNAT project to a PACS destination')
    parser.add_argument('config', metavar='N', type=str, help='Path to config file describing project (yml)')
    args = parser.parse_args()

    config = parse_config_yml(args.config)

    send_to_pacs(config)
