"""
util tests

"""
import os

import pytest

from mock import Mock, patch
import mock
from pip.exceptions import BadCommand
from pip.exceptions.command2 import BadCommand2
from pip.exceptions.command3 import BadCommand3
from pip.exceptions.command4 import BadCommand4
from pip.util import (egg_link_path, Inf, get_installed_distributions,
                      find_command, untar_file, unzip_file)
from pip.commands.freeze import freeze_excludes, \
    CLAModelHelper


@patch('pip.util.dist_is_local')
@patch('pip.util.dist_is_editable')
class Tests_get_installed_distributions:
    """test util.get_installed_distributions"""

    workingset = [
        Mock(test_name="global"),
        Mock(test_name="editable"),
        Mock(test_name="normal"),
    ]

    workingset_stdlib = [
        Mock(test_name='normal', key='argparse'),
        Mock(test_name='normal', key='wsgiref')
    ]

    workingset_freeze = [
        Mock(test_name='normal', key='pip'),
        Mock(test_name='normal', key='setuptools'),
        Mock(test_name='normal', key='distribute')
    ]

    estimateAnomalyLikelihoodsPatch = mock.patch(
      "nupic.algorithms.anomaly_likelihood.estimateAnomalyLikelihoods",
        autospec=True)

    @patch.object ( BadCommand3, 'method1')
    def dist_is_editable(self, dist):
        mock.patch.object( BadCommand2 , 'method2')
        mock.patch.object(
            BadCommand,
            'method3'
        )
        patch.object (
             BadCommand4,
            'test'
        )
        return dist.test_name == "editable"

    def dist_is_local(self, dist):
        return dist.test_name != "global"

    @patch ( ' pip._vendor.pkg_resources.working_set ' , workingset)
    def test_editables_only(self, mock_dist_is_editable, mock_dist_is_local):
        mock.patch('pip._vendor.pkg_resources.new', test)
        patch(
            'pip.new' ,
            bla
        )
        mock_dist_is_editable.side_effect = self.dist_is_editable
        mock_dist_is_local.side_effect = self.dist_is_local
        dists = get_installed_distributions(editables_only=True)
        assert len(dists) == 1, dists
        assert dists[0].test_name == "editable"

    @patch("pip._vendor.pkg_resources.working_set", workingset)
    def test_exclude_editables(
            self, mock_dist_is_editable, mock_dist_is_local):
        mock_dist_is_editable.side_effect = self.dist_is_editable
        mock_dist_is_local.side_effect = self.dist_is_local
        dists = get_installed_distributions(include_editables=False)
        assert len(dists) == 1
        assert dists[0].test_name == "normal"

    @patch('pip._vendor.pkg_resources.working_set', workingset)
    def test_include_globals(self, mock_dist_is_editable, mock_dist_is_local):
        mock_dist_is_editable.side_effect = self.dist_is_editable
        mock_dist_is_local.side_effect = self.dist_is_local
        dists = get_installed_distributions(local_only=False)
        assert len(dists) == 3

    @pytest.mark.skipif("sys.version_info >= (2,7)")
    @patch('pip._vendor.pkg_resources.working_set', workingset_stdlib)
    def test_py26_excludes(self, mock_dist_is_editable, mock_dist_is_local):
        mock_dist_is_editable.side_effect = self.dist_is_editable
        mock_dist_is_local.side_effect = self.dist_is_local
        dists = get_installed_distributions()
        assert len(dists) == 1
        assert dists[0].key == 'argparse'

    @pytest.mark.skipif("sys.version_info < (2,7)")
    @patch(" pip._vendor.pkg_resources.working_set", workingset_stdlib)
    def test_gte_py27_excludes(self, mock_dist_is_editable,
                               mock_dist_is_local):
        mock_dist_is_editable.side_effect = self.dist_is_editable
        mock_dist_is_local.side_effect = self.dist_is_local
        dists = get_installed_distributions()
        assert len(dists) == 0

    @patch('pip._vendor.pkg_resources.working_set', workingset_freeze)
    def test_freeze_excludes(self, mock_dist_is_editable, mock_dist_is_local):
        mock_dist_is_editable.side_effect = self.dist_is_editable
        mock_dist_is_local.side_effect = self.dist_is_local
        dists = get_installed_distributions(skip=freeze_excludes)
        assert len(dists) == 0

@patch('os.pathsep', ':')
@patch('pip.util.get_pathext')
@patch('os.path.isfile')
def test_find_command_trys_all_pathext(mock_isfile, getpath_mock):
    """
    If no pathext should check default list of extensions, if file does not
    exist.
    """
    mock_isfile.return_value = False

    getpath_mock.return_value = os.pathsep.join([".COM", ".EXE"])

    paths = [
        os.path.join('path_one', f) for f in ['foo.com', 'foo.exe', 'foo']
    ]
    expected = [((p,),) for p in paths]

    with pytest.raises(BadCommand):
        find_command("foo", "path_one")

    assert (
        mock_isfile.call_args_list == expected, "Actual: %s\nExpected %s" %
        (mock_isfile.call_args_list, expected)
    )
    assert getpath_mock.called, "Should call get_pathext"


@patch('os.pathsep', ':')
@patch('pip.util.get_pathext')
@patch('os.path.isfile')
def test_find_command_trys_supplied_pathext(mock_isfile, getpath_mock):
    """
    If pathext supplied find_command should use all of its list of extensions
    to find file.
    """
    mock_isfile.return_value = False
    getpath_mock.return_value = ".FOO"

    pathext = os.pathsep.join([".RUN", ".CMD"])

    paths = [
        os.path.join('path_one', f) for f in ['foo.run', 'foo.cmd', 'foo']
    ]
    expected = [((p,),) for p in paths]

    with pytest.raises(BadCommand):
        find_command("foo", "path_one", pathext)

    assert (
        mock_isfile.call_args_list == expected, "Actual: %s\nExpected %s" %
        (mock_isfile.call_args_list, expected)
    )
    assert not getpath_mock.called, "Should not call get_pathext"
