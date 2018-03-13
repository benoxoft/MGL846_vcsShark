import argparse
import logging
import logging.config
import os
import sys


from testimpshark.common import setup_logging, get_all_immidiate_folders
from testimpshark.evoshark import EvoSHARK


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


def detect_mock_paths(logger):
    mock_paths = []
    for path in sys.path:
        if os.path.isdir(path):
            folders = get_all_immidiate_folders(path)
            if 'mock' in folders:
                mock_paths.append(os.path.join(path, 'mock'))

    if mock_paths is None:
        logger.error("Install mock package first!")
        sys.exit(1)

    return mock_paths

def start():
    """ Start method to start the program. It first sets up the logging and then parses all the arguments
    it got from the comandline.

    .. NOTE::
       String format for the commands (repc, revc, fc): command1,command2,command3
       For example:
       /home/user1/test/test.py 1 3 3 7 4 2 output,find /home/user2 -name '*.class' -print
    """

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
    parser.add_argument('-r', '--rev', help='Revision hash that should be processed', required=True)
    parser.add_argument('-i', '--input', help='Path to the revision in the corresponding hash', required=True)

    logger.info("Reading out config from command line")

    try:
        args = parser.parse_args()
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    mock_paths = detect_mock_paths(logger)

    evoshark = EvoSHARK(args.output_dir, args.url, args.db_database, args.db_hostname, args.db_port,
                        args.db_authentication, args.db_user, args.db_password, mock_paths)
    evoshark.process_revision(args.rev, args.input)
if __name__ == "__main__":
    start()