import os
import pygit2
import logging
import re
import shutil
import time

class Repository(object):

    def __init__(self, config):
        self.logger = logging.getLogger("repository_processor")
        self.config = config
        self.repository = None

        # Get name of the project (last part of the output path)
        self.project_name = os.path.basename(os.path.normpath(self.config.output_dir))
        self.clone_path = os.path.join(config.output_dir, 'base')

    def clone_repository(self):
        shutil.rmtree(self.clone_path, True)

        # Clone repository into the folder
        self.logger.info("Cloning project %s into %s" % (self.project_name, self.clone_path))
        self.repository = pygit2.clone_repository(self.config.url, self.clone_path)

    def set_repository_to_version(self, version_hash):
        error_occ = True
        while error_occ:
            try:
                self.repository.reset(version_hash, pygit2.GIT_RESET_HARD)
                error_occ = False
            except pygit2.GitError:
                time.sleep(2)
                error_occ = True
            except OSError:
                time.sleep(2)
                error_occ = True

    def discover_repository(self, path):
        discovered_path = pygit2.discover_repository(path)
        self.repository = pygit2.Repository(discovered_path)

    def get_all_versions(self):
        # Get all references (branches, tags)
        references = set(self.repository.listall_references())

        # Get all tags
        regex = re.compile('^refs/tags')
        tags = set(filter(lambda r: regex.match(r), self.repository.listall_references()))

        # Get all branches
        branches = references-tags
        commits = set()

        self.logger.info("Getting branch information...")
        for branch in branches:
            self.logger.info("Getting information from branch %s" % branch)
            commit = self.repository.lookup_reference(branch).peel()

            # Walk through every child
            for child in self.repository.walk(commit.id, pygit2.GIT_SORT_REVERSE | pygit2.GIT_SORT_TIME):
                commits.add(str(child.id))

        return sorted(commits)



