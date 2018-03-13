import tests.data.project2.module.package1.sub_package1.module1
from tests.data.project2.module.package1.module2 import Module2
import tests.data.project2.module.package2.module3
from mock import patch


@patch ( ' tests.data.project2.module.package2.module3 ' , '')
def test_method():
    pass
