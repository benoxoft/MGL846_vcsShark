import argparse
import os
import sys
from .config import Config
from .main import Application
from .utils import *
import json
import logging
import logging.config
from pyvcsshark.datastores.basestore import BaseStore


def setup_logging(default_path=os.path.dirname(os.path.realpath(__file__))+"/loggerConfiguration.json", 
                  default_level=logging.INFO):
        """
        Setup logging configuration
        
        :param default_path: path to the logger configuration
        :param default_level: defines the default logging level if configuration file is not found (default: logging.INFO)
        """
        path = default_path
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = json.load(f)
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)
            
def getDatastoreChoices():
    """ Helper function that gets all the available datastore choices, so that
    we can check, if the user chooses an available datastore.
    """
    
    # Helper function, that imports all .py files in the datastores folder
    find_plugins(os.path.dirname(os.path.realpath(__file__))+"/datastores")
    choices = []
    for sc in BaseStore.__subclasses__():
        datastore = sc()
        choices.append(datastore.storeIdentifier)
    return choices
        
        
def start():
    """ Start method to start the program. It first sets up the logging and then parses all the arguments
    it got from the comandline. If a config file was given, the values in the config file overwrite the ones
    given on the commandline.
    
    .. WARNING::
       If a configuration file is specified, it will overwrite the values given via the commandline!
    """
    
    setup_logging()
    logger = logging.getLogger("main")
    
    datastoreChoices = None
    try:
        datastoreChoices = getDatastoreChoices()
    except Exception as e:
        logger.error("Failed to instantiate datastore. Original message: %s" % (e))
        sys.exit(1)
        
    if(not datastoreChoices):
        logger.error("No datastores found! Exiting...")
        sys.exit(1)
                
    parser = argparse.ArgumentParser(description='Analyze the given URI. An URI can be a checked out directory. \
                                                 If URI is omitted, the current working directory will be used as a checked out directory.')
    parser.add_argument('-v', '--version', help='Shows the version', action='version', version='0.0.1')
    parser.add_argument('-f', '--config-file', help='Path to a custom configuration file', default=None)
    parser.add_argument('-D', '--db-driver', help='Output database driver. Currently only mongoDB is supported', default='mongo', choices=datastoreChoices)
    parser.add_argument('-DB', '--db-database', help='Database name', default='smartshark')
    parser.add_argument('-H', '--db-hostname', help='Name of the host, where the database server is running', default='localhost')
    parser.add_argument('-p', '--db-port', help='Port, where the database server is listening', default=27017, type=int)
    parser.add_argument('--path', help='Path to the checked out repository directory', default=os.getcwd(), type=readable_dir)
    parser.add_argument('-n', '--project-name', help='Name of the project, that is analyzed', required=True)

    logger.info("Reading out config from command line")

    try:
        args = parser.parse_args()
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    config = Config(args.project_name,
                    args.db_driver,
                    args.db_database,
                    args.db_hostname,
                    args.db_port,
                    args.path
                    )
    
    # If config file was specified, overwrite the values
    if(args.config_file != None):
        try:
            logger.info("Found config file... read configuration file")
            config.load_from_file(args.config_file)
        except Exception as e:
            logger.error(e)
            sys.exit(1)

    Application(config)
