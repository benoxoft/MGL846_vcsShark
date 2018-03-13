import unittest
import os
import re

class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.file1_path = os.path.join(os.path.dirname(__file__), 'data', 'mock_detection', 'file1.py')
        cls.file2_path = os.path.join(os.path.dirname(__file__), 'data', 'mock_detection', 'file2.py')

        cls.regex_for_class_mock_detection = re.compile('(?:@patch\.object|patch\.object)\s*\(\s*(\w*)\s*\,')
        cls.regex_for_patch_mock_detection = re.compile("(?:@patch|mock\.patch|patch)\s*\(\s*(?:\'|\")\s*([\w\.]*)")

    def test_regex_detection(self):

        with open(self.file1_path, 'r') as f:
            contents = f.read()
        #print(contents.replace('\n',' '))
        m1 = re.findall(self.regex_for_patch_mock_detection, contents.replace('\n', ' '))
        m2 = re.findall(self.regex_for_class_mock_detection, contents.replace('\n', ' '))

        expected_set = []
        expected_set.append('pip.util.dist_is_local')
        expected_set.append('pip.util.dist_is_editable')
        expected_set.append('nupic.algorithms.anomaly_likelihood.estimateAnomalyLikelihoods')
        expected_set.append('pip._vendor.pkg_resources.working_set')
        expected_set.append('pip._vendor.pkg_resources.new')
        expected_set.append('pip.new')
        expected_set.append('pip._vendor.pkg_resources.working_set')
        expected_set.append('pip._vendor.pkg_resources.working_set')
        expected_set.append('pip._vendor.pkg_resources.working_set')
        expected_set.append('pip._vendor.pkg_resources.working_set')
        expected_set.append('pip._vendor.pkg_resources.working_set')
        expected_set.append('os.pathsep')
        expected_set.append('pip.util.get_pathext')
        expected_set.append('os.path.isfile')
        expected_set.append('os.pathsep')
        expected_set.append('pip.util.get_pathext')
        expected_set.append('os.path.isfile')
        self.assertListEqual(m1, expected_set)

        expected_set = []
        expected_set.append('BadCommand3')
        expected_set.append('BadCommand2')
        expected_set.append('BadCommand')
        expected_set.append('BadCommand4')
        self.assertListEqual(m2, expected_set)


if __name__ == '__main__':
    unittest.main()
