#!/usr/local/bin/python3

'''delete-sessions.py

Usage:
    python3 delete-sessions.py PROJECT

Options:
    PROJECT

'''

import xnat
import logging
import time
import getpass
import sys

logging.basicConfig(level=logging.INFO)


project = sys.argv[1]
user = getpass.getuser()
user = input('Enter your XNAT username: ')
password = getpass.getpass()


def delete_project(xnat_configuration: dict):
    """
    Main function, creates xnat session and sends all subjects to destination
    :param project: name of project to delete (label in xnat)
    :param xnat_configuration: dictionary with keys 'server', 'user', 'password', 'project', 'verify'
    :return:
    """

    with xnat.connect(server=xnat_configuration['server'],
                      user=xnat_configuration['user'],
                      password=xnat_configuration['password'],
                      verify=xnat_configuration['verify'],
                      ) as session:
        project = session.projects[xnat_configuration["project"]]
        logging.info(f'You have logged in as {user}.')
        logging.info(f'You have selected to delete all subjects in {project}.')
        input("Press enter to start subject deletion. This process is interruptable with ctr+c command.)")
        print('Deleting will start now.')

        logging.info(f'Deleting data in project {project}:')
        for subject in project.subjects.values():
            logging.info(f'\tSubject: {subject}')
            subject.delete()
            time.sleep(1)


if __name__ == '__main__':
    xnat_configuration = {'server': 'http://localhost',
                          'user': user,
                          'password': password,
                          'project' : project,
                          'verify': 'false'}


    delete_project(xnat_configuration)
