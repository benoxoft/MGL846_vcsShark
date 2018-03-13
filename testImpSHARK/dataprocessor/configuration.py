import logging


class Configuration(object):

    def __init__(self, url, output_dir, db_user, db_password, db_database, db_hostname, db_port, db_auth, force):
        self.logger = logging.getLogger("main")
        self.url = url
        self.output_dir = output_dir
        self.db_user = db_user
        self.db_password = db_password
        self.db_database = db_database
        self.db_hostname = db_hostname
        self.db_port = int(db_port)
        self.db_auth = db_auth
        self.force_renew = force

        if url.endswith('/'):
            url = url[:-1]

        self.project_name = url.rsplit('/', 1)[-1]

    @staticmethod
    def parse_types(types):
        if not types:
            return []

        return types.split(",")

    def __str__(self):
        return 'Url: %s, Output: %s, User: %s, Password: %s, Database: %s, Hostname: %s, Port: %s, Auth: %s,' \
               ' Force_renew: %s' % (self.url, self.output_dir, self.db_user, self.db_password,
                                                  self.db_database, self.db_hostname, str(self.db_port), self.db_auth,
                                                  self.force_renew)
