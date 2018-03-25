import logging


class Configuration(object):

    def __init__(self,
                 project_name,
                 url,
                 output_dir,
                 db_database,
                 db_hostname,
                 db_port,
                 force
                 ):
        self.logger = logging.getLogger("main")
        self.project_name = project_name
        self.url = url
        self.output_dir = output_dir
        self.db_database = db_database
        self.db_hostname = db_hostname
        self.db_port = int(db_port)
        self.force_renew = force

        if url.endswith('/'):
            url = url[:-1]

    @staticmethod
    def parse_types(types):
        if not types:
            return []

        return types.split(",")
