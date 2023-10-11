# This script allows you to delete large projects on XNAT one subject at a time. You will need this file
# and a config.yml file to do so. The config.yml example is stored in xnat-csc/src/delete/config in XNAT repo.
# You will need to run this from the terminal. First set your XNAT password as an environment variable with command
# export XNAT_PASSWORD=yourpassword
# Then update the config.yml with your xnat username and your project ID
# Then run this script with
# python3 delete-sessions.py config.yml
# This script is interruptable with ctrl + c. It will delete subjects one at a time

import xnat
import logging
import time
import argparse
import re
import os
import yaml

logging.basicConfig(level=logging.INFO)


def delete_sessions(config):
    """
    Use the configuration information stored in config
    :param config:
    :return:
    """

    with xnat.connect(
        server=config["xnat"]["url"],
        user=config["xnat"]["user"],
        password=config["xnat"]["password"],
        verify=config["xnat"]["verify"] if "verify" in config["xnat"] else False,
        loglevel="ERROR",
    ) as session:
        logging.info(f"Opened XNAT Session: {session}")
        project = session.projects[config["xnat"]["project_id"]]
        logging.info(f'You have selected to delete all subjects in {project}.')
        input("Press enter to start subject deletion. This process is interruptable with ctr+c command.)")
        print('Deleting will start now.')

        logging.info(f'Deleting data in project {project}:')
        for subject in project.subjects.values():
            logging.info(f'\tSubject: {subject}')
            subject.delete()
            time.sleep(1)


def parse_config_yml(yml_path):
    path_matcher = re.compile(r"\$\{([^}^{]+)}")

    def path_constructor(loader, node):
        """Extract the matched value, expand env variable, and replace the match"""
        value = node.value
        match = path_matcher.match(value)
        env_var = match.group()[2:-1]
        return os.environ.get(env_var) + value[match.end() :]

    yaml.add_implicit_resolver("!path", path_matcher, None, yaml.SafeLoader)
    yaml.add_constructor("!path", path_constructor, yaml.SafeLoader)

    with open(yml_path, "r") as stream:
        try:
            conf = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return conf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send XNAT project to a PACS destination"
    )
    parser.add_argument(
        "config",
        metavar="N",
        type=str,
        help="Path to config file describing project (yml)",
    )
    args = parser.parse_args()

    config = parse_config_yml(args.config)

    delete_sessions(config)
