import argparse
import re
import os
import xnat
from tqdm import tqdm
import logging
import time
import yaml

logging.basicConfig(level=logging.INFO)


def send_to_pacs(config):
    """
    Sends an XNAt project to pacs using the configuration information stored in config
    :param config:
    :return:
    """

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

        for subject in tqdm(project.subjects.values()):
            logging.debug(f'Subject: {subject}')
            # Add subject level inclusion/exclusion criteria here

            for experiment in subject.experiments.values():
                logging.debug(f'\tExperiment: {experiment}')
                # Add experiment level inclusion/exclusion criteria here

                for scan in experiment.scans.values():
                    logging.debug(f'\tScan: {experiment}')
                    # Add scan level inclusion/exclusion criteria here

                    for attempt in range(config['settings']['attempts'] if 'attempts' in config['settings'] else 1):
                        try:
                            if not check_criteria(scan, config['criteria']['inclusion']['scan']):
                                break
                            response = session.put('/xapi/dqr/export/', query={'pacsId': pacs['id'], 'session': experiment.id, 'scansToExport': scan.id})
                            logging.debug(response)
                            if 'complete_log' in config['settings']:
                                with open(config['settings']['complete_log'], "a") as f:
                                    f.write(f"{subject},{experiment},{scan}\n")

                        except InclusionException as e:
                            # If inclusion criteria raises exception no need to retry
                            last_e = e
                            logging.warning(f"FAILED after {attempt} attempts: {subject}, {experiment}, {scan}; exception: {last_e}")
                            log_failures(f"{subject},{experiment},{scan},{last_e}", config)
                            break

                        except Exception as e:
                            # all other exceptions result in retries
                            last_e = e
                            logging.warning(f'RETRYING - {attempt+1}; exception: {e}')

                        else:
                            break

                        finally:
                            time.sleep(config['settings']['delay'])

                    else:
                        # all attempts failed
                        logging.warning(f"FAILED after {config['settings']['attempts']} attempts: {subject}, {experiment}, {scan}; exception: {last_e}")
                        log_failures(f"{subject},{experiment},{scan},{last_e}", config)


class InclusionException(Exception):
    """There was an error assessing this file against inclusion criteria"""


def log_failures(msg, config):
    if 'failure_log' in config['settings']:
        with open(config['settings']['failure_log'], "a") as f:
            f.write(f"{msg}\n")


def check_criteria(xnat_obj, criteria) -> bool:
    """
    Checks the criteria against the xnat_obj - if any condition evaluates to True the function returns True
    :param xnat_obj:
    :param criteria:
    :return:
    """
    try:
        for condition in criteria:
            values = list(condition['value'])
            state = [xnat_obj.data[condition['field']] == val for val in values]
        if any(state):
            return True
        else:
            return False
    except Exception as e:
        raise InclusionException(f'There was an error assessing this file against inclusion criteria {e}')


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
