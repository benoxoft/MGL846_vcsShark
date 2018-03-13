import argparse
import logging
import logging.config
import os
import shutil
import sys
import subprocess
from string import Template

from dataprocessor.configuration import Configuration
from dataprocessor.repository import Repository
from testimpshark.common import setup_logging


def writable_dir(prospective_dir):
    """ Function that checks if a path is a directory, if it exists and if it is writable and only
    returns true if all these three are the case

    :param prospective_dir: path to the directory"""
    if prospective_dir is not None:
        if not os.path.isdir(prospective_dir):
            os.makedirs(prospective_dir, exist_ok=True)
        if os.access(prospective_dir, os.W_OK):
            return prospective_dir
        else:
            raise Exception("readable_dir:{0} is not a writable dir".format(prospective_dir))


def execute(config, logger, revision, path_to_revision_dump):
    """
    We need this wrapper, as projects can be written in different python versions. Therefore, the correct python call
    must be made, as the modulefinder library is not working otherwise


    :param config: execution config
    :param logger: logger factory
    :param revision: revision that is processed
    :param path_to_revision_dump: path to the revision
    :return:
    """
    orig_command = '$python %s -u %s -out %s -U %s -P %s -DB %s -H %s -p %s -a %s -r %s -i %s' % \
                  (os.path.dirname(__file__)+"/main.py", config.url, config.output_dir, config.db_user,
                   config.db_password, config.db_database, config.db_hostname, config.db_port, config.db_auth,
                   revision, path_to_revision_dump)

    error_occured = True
    retry = 0
    command = Template(orig_command).safe_substitute(python='python2.7')
    while error_occured:
        if retry == 1:
            command = Template(orig_command).safe_substitute(python='python3.5')

        if retry > 1:
            logger.error('Revision was not processed: %s' % revision)
            break

        try:
            logger.info('Calling command: %s' % command)
            completed = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            error_occured = False
            logger.debug(completed.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(e.output)
            retry += 1

    shutil.rmtree(path_to_revision_dump)


def start():
    setup_logging()
    logger = logging.getLogger("main")

    parser = argparse.ArgumentParser(description='Prepares the execution of plugins by downloading the projects.')
    parser.add_argument('-v', '--version', help='Shows the version', action='version', version='0.0.1')
    parser.add_argument('-u', '--url', help='URL to the repository, that can be directly cloned.',
                        required=True)
    parser.add_argument('-out', '--output_dir', help='Directory, which can be used as output.',
                        required=True, type=writable_dir)
    parser.add_argument('-U', '--db-user', help='Database user name', default='root')
    parser.add_argument('-P', '--db-password', help='Database user password', default='root')
    parser.add_argument('-DB', '--db-database', help='Database name', default='smartshark')
    parser.add_argument('-H', '--db-hostname', help='Name of the host, where the database server is running', default='localhost')
    parser.add_argument('-p', '--db-port', help='Port, where the database server is listening', default=27017, type=int)
    parser.add_argument('-a', '--db-authentication', help='Name of the authentication database')
    parser.add_argument('-f', '--force', help='Forces the renewing of all revisions.', action='store_true')

    logger.info("Reading out config from command line")

    try:
        args = parser.parse_args()
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    config = Configuration(args.url, args.output_dir, args.db_user, args.db_password, args.db_database, args.db_hostname,
                           args.db_port, args.db_authentication, args.force)

    logger.debug('Read the following config: %s' % config)

    # Set repository and clone newest one
    repository = Repository(config)
    repository.clone_repository()

    path_to_repository_dump = os.path.join(config.output_dir, 'repo')

    # if folder is already existent: delete it:
    if os.path.isdir(path_to_repository_dump):
        logger.info("Delete folder %s." % path_to_repository_dump)
        shutil.rmtree(path_to_repository_dump)

    logger.info("Copying repository from %s to %s." % (repository.clone_path, path_to_repository_dump))
    shutil.copytree(repository.clone_path, path_to_repository_dump, symlinks=True, ignore_dangling_symlinks=True)

    logger.info("Copying and setting all versions")

    for revision in repository.get_all_versions():
        logger.info("Executing on revision: %s" % revision)

        path_to_revision_dump = os.path.join(config.output_dir, 'rev', revision)

        if os.path.isdir(path_to_revision_dump):
            if config.force_renew:
                shutil.rmtree(path_to_revision_dump)
        else:
            shutil.copytree(repository.clone_path, path_to_revision_dump, symlinks=True, ignore_dangling_symlinks=True)

        repository.discover_repository(path_to_revision_dump)

        try:
            repository.set_repository_to_version(revision)
        except KeyError:
            logger.error("Key error for revision %s." % revision)
            continue
        execute(config, logger, revision, path_to_revision_dump)



if __name__ == "__main__":
    start()
