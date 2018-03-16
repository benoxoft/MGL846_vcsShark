import unittest
import json
import os
import sys
from modulefinder import ModuleFinder, Module

from modulegraph.modulegraph import ModuleGraph, Package, SourceModule
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from testimpshark.common import get_all_immidiate_folders
from testimpshark.testimpshark import TestImpSHARK
from testimpshark.newmodulefinder.newmodulefinder_python35 import NewModuleFinder


class EvoSHARKTest(unittest.TestCase):
    @staticmethod
    def prepare_database(url, db, hostname, port, auth, user, password):
        try:
            client = MongoClient('%s:%s' % (hostname, port))
            client[auth].authenticate(user, password)
            client[db].get_collection('project').insert_one({'url': url})
        except DuplicateKeyError:
            pass


    @classmethod
    def setUpClass(cls):
        with open(os.path.dirname(os.path.realpath(__file__))+"/config.json", 'r') as data_file:
            read_config = json.load(data_file)

        output_dir = os.path.realpath(__file__)+read_config['output_dir']

        cls.prepare_database(read_config['url'], read_config['db_database'], read_config['db_hostname'],
                             read_config['db_port'], read_config['db_auth'], read_config['db_user'],
                             read_config['db_password'])
        cls.mock_paths = cls.get_mock_paths(cls)
        cls.evo_shark = TestImpSHARK(output_dir, read_config['url'], read_config['db_database'],
                                 read_config['db_hostname'], read_config['db_port'], read_config['db_auth'],
                                 read_config['db_user'], read_config['db_password'], cls.mock_paths)

        cls.project2_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__))+"/../tests/data/project2")

        cls.path_to_main_program_root = os.path.abspath(os.path.dirname(os.path.realpath(__file__))+"/../")
        cls.path_to_module_of_project2 = os.path.join(cls.project2_path, 'module')
        cls.path_to_tests_of_project_2 = os.path.join(cls.project2_path, 'tests')

        cls.path_for_search = [cls.path_to_main_program_root]

        cls.path_for_search.extend(cls.mock_paths)
        cls.path_to_test_1 = os.path.abspath(os.path.join(cls.path_to_tests_of_project_2, 'test1.py'))
        cls.path_to_test_2 = os.path.abspath(os.path.join(cls.path_to_tests_of_project_2, 'test2.py'))
        cls.path_to_test_3 = os.path.abspath(os.path.join(cls.path_to_tests_of_project_2, 'test3.py'))
        cls.path_to_test_4 = os.path.abspath(os.path.join(cls.path_to_tests_of_project_2, 'test4.py'))
        cls.path_to_test_5 = os.path.abspath(os.path.join(cls.path_to_tests_of_project_2, 'test5.py'))

        cls.current_files = cls.evo_shark.get_all_files_in_current_revision(cls.path_to_main_program_root)

        cls.base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))


    def get_mock_paths(self):
        mock_paths = []
        for path in sys.path:
            if os.path.isdir(path):
                folders = get_all_immidiate_folders(path)
                if 'mock' in folders:
                    mock_paths.append(os.path.join(path, 'mock'))
        return mock_paths

    def test_get_direct_imports(self):
        new_finder = NewModuleFinder(self.path_for_search)
        direct_imports = self.evo_shark.get_direct_imports(new_finder, self.path_to_test_1, self.project2_path)
        expected_modules = [
            # first, all init.py must be there
            Module('tests.data.project2', self.base_path+'/tests/data/project2/__init__.py'),
            Module('tests.data.project2.module',  self.base_path+'/tests/data/project2/module/__init__.py'),
            Module('tests.data.project2.module.package1',  self.base_path+'/tests/data/project2/module/package1/__init__.py'),
            Module('tests.data.project2.module.package1.sub_package1', self.base_path+'/tests/data/project2/module/package1/sub_package1/__init__.py'),
            Module('tests.data.project2.module.package2', self.base_path+'/tests/data/project2/module/package2/__init__.py'),

            # Now the other modules
            Module('tests.data.project2.module.package1.sub_package1.module1',  self.base_path+'/tests/data/project2/module/package1/sub_package1/module1.py'),
            Module('tests.data.project2.module.package1.module2',  self.base_path+'/tests/data/project2/module/package1/module2.py'),
            Module('tests.data.project2.module.package2.module3',  self.base_path+'/tests/data/project2/module/package2/module3.py'),
        ]

        self.assertTrue(self.checkEqualModuleList(direct_imports, expected_modules))

    def test_get_dep_modules(self):
        finder = ModuleFinder(self.path_for_search)
        new_finder = NewModuleFinder(self.path_for_search)
        modules, direct_imports, uses_mock, mocked_modules = \
            self.evo_shark.get_dep_modules(finder, new_finder, self.path_to_test_1, self.project2_path, self.current_files)

        expected_direct_imports = [
            # first, all init.py must be there
            Module('tests.data.project2',  self.base_path+'/tests/data/project2/__init__.py'),
            Module('tests.data.project2.module',  self.base_path+'/tests/data/project2/module/__init__.py'),
            Module('tests.data.project2.module.package1',  self.base_path+'/tests/data/project2/module/package1/__init__.py'),
            Module('tests.data.project2.module.package1.sub_package1',  self.base_path+'/tests/data/project2/module/package1/sub_package1/__init__.py'),
            Module('tests.data.project2.module.package2',  self.base_path+'/tests/data/project2/module/package2/__init__.py'),

            # Now the other modules
            Module('tests.data.project2.module.package1.sub_package1.module1',  self.base_path+'/tests/data/project2/module/package1/sub_package1/module1.py'),
            Module('tests.data.project2.module.package1.module2',  self.base_path+'/tests/data/project2/module/package1/module2.py'),
            Module('tests.data.project2.module.package2.module3',  self.base_path+'/tests/data/project2/module/package2/module3.py'),
        ]

        expected_modules = [
            Module('tests.data.project2.module.package2.module4', self.base_path+'/tests/data/project2/module/package2/module4.py')
        ]

        self.assertTrue(self.checkEqualModuleList(direct_imports, expected_direct_imports))
        self.assertTrue(self.checkEqualModuleList(modules, expected_modules))
        self.assertFalse(uses_mock)
        self.assertFalse(mocked_modules)

    def test_get_what_is_mocked(self):
        # go through test 2 - test 5, which all mock module3 but differently
        mocked_test_2 = self.evo_shark.get_what_is_mocked(self.path_to_test_2, self.project2_path, self.current_files)
        mocked_test_3 = self.evo_shark.get_what_is_mocked(self.path_to_test_3, self.project2_path, self.current_files)
        mocked_test_4 = self.evo_shark.get_what_is_mocked(self.path_to_test_4, self.project2_path, self.current_files)
        mocked_test_5 = self.evo_shark.get_what_is_mocked(self.path_to_test_5, self.project2_path, self.current_files)

        expected_mocked_module = set([Module('tests.data.project2.module.package2.module3', 'tests/data/project2/module/package2/module3.py')])
        self.assertTrue(self.checkEqualModuleList(mocked_test_2, expected_mocked_module))
        self.assertTrue(self.checkEqualModuleList(mocked_test_3, expected_mocked_module))
        self.assertTrue(self.checkEqualModuleList(mocked_test_4, expected_mocked_module))
        self.assertTrue(self.checkEqualModuleList(mocked_test_5, expected_mocked_module))


    def test_get_dependencies_with_mock_cutoff(self):
        # go throught test 2 - test 5, which all mock module3 but differently
        graph = ModuleGraph(self.path_for_search)

        expected_mock_cutoff = [
            Package('tests.data.project2', self.base_path+'/tests/data/project2/__init__.py'),
            Package('tests.data.project2.module', self.base_path+'/tests/data/project2/module/__init__.py'),
            Package('tests.data.project2.module.package1', self.base_path+'/tests/data/project2/module/package1/__init__.py'),
            Package('tests.data.project2.module.package1.sub_package1', self.base_path+'/tests/data/project2/module/package1/sub_package1/__init__.py'),
            SourceModule('tests.data.project2.module.package1.module2', self.base_path+'/tests/data/project2/module/package1/module2.py'),
            SourceModule('tests.data.project2.module.package1.sub_package1.module1', self.base_path+'/tests/data/project2/module/package1/sub_package1/module1.py'),
        ]
        mock_cutoff_test_2 = self.evo_shark.get_dependencies_with_mock_cutoff(graph, self.path_to_test_2, self.project2_path,
                                                                              ['tests.data.project2.module.package2.module3'])
        mock_cutoff_test_3 = self.evo_shark.get_dependencies_with_mock_cutoff(graph, self.path_to_test_3, self.project2_path,
                                                                              ['tests.data.project2.module.package2.module3'])
        mock_cutoff_test_4 = self.evo_shark.get_dependencies_with_mock_cutoff(graph, self.path_to_test_4, self.project2_path,
                                                                              ['tests.data.project2.module.package2.module3'])
        mock_cutoff_test_5 = self.evo_shark.get_dependencies_with_mock_cutoff(graph, self.path_to_test_5, self.project2_path,
                                                                              ['tests.data.project2.module.package2.module3'])

        self.assertTrue(self.checkEqualModuleListFromModulegraph(mock_cutoff_test_2, expected_mock_cutoff))
        self.assertTrue(self.checkEqualModuleListFromModulegraph(mock_cutoff_test_3, expected_mock_cutoff))
        self.assertTrue(self.checkEqualModuleListFromModulegraph(mock_cutoff_test_4, expected_mock_cutoff))
        self.assertTrue(self.checkEqualModuleListFromModulegraph(mock_cutoff_test_5, expected_mock_cutoff))



    def checkEqualModuleList(self, L1, L2):
        sorted_l1 = sorted(L1, key=lambda x: x.__file__)
        sorted_l2 = sorted(L2, key=lambda x: x.__file__)

        if len(sorted_l1) != len(sorted_l2):
            return False

        for i in range(0, len(sorted_l1)):
            if sorted_l1[i].__name__ != sorted_l2[i].__name__ or sorted_l1[i].__file__ != sorted_l2[i].__file__:
                return False

        return True

    def checkEqualModuleListFromModulegraph(self, L1, L2):
        sorted_l1 = sorted(L1, key=lambda x: x.filename)
        sorted_l2 = sorted(L2, key=lambda x: x.filename)

        if len(sorted_l1) != len(sorted_l2):
            return False

        for i in range(0, len(sorted_l1)):
            if sorted_l1[i].identifier != sorted_l2[i].identifier or sorted_l1[i].filename != sorted_l2[i].filename:
                return False

        return True

if __name__ == '__main__':
    unittest.main()
