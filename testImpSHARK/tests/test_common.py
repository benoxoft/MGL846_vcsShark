import unittest
import os

from testimpshark.common import get_all_immidiate_folders


class CommonTest(unittest.TestCase):
    def test_get_all_immediate_folders(self):
        self.assertTrue(self.checkEqual(
            get_all_immidiate_folders(os.path.dirname(os.path.realpath(__file__))+"/data"),
            ['project1', 'project2', 'mock_detection']
        ))

    def checkEqual(self, L1, L2):
        return len(L1) == len(L2) and sorted(L1) == sorted(L2)

if __name__ == '__main__':
    unittest.main()
