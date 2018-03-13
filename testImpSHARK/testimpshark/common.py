import logging
import os
import logging.config
import json


def setup_logging(default_path=os.path.dirname(os.path.realpath(__file__))+"/loggerConfiguration.json",
                  default_level=logging.INFO):
        """
        Setup logging configuration

        :param default_path: path to the logger configuration
        :param default_level: defines the default logging level if configuration file is not found
        (default:logging.INFO)
        """
        path = default_path
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = json.load(f)
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)


def get_all_immidiate_folders(root):
    sub_dirs = []
    for entry in os.listdir(root):
        if not entry.startswith('.git') and os.path.isdir(os.path.join(root, entry)):
            sub_dirs.append(entry)
    return sub_dirs

def get_all_folders(input_path):
    sub_dirs = []
    for root, dirs, files in os.walk(input_path):
        if ".git" not in root:
            sub_dirs.append(root)
    return sub_dirs