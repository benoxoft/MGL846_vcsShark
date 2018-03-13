import tests.data.project2.module.package1.sub_package1.module1
from tests.data.project2.module.package1.module2 import Module2
from tests.data.project2.module.package2.module3 import Module3
from mock import patch


@patch.object ( Module3, 'method1')
def test_method():
    pass