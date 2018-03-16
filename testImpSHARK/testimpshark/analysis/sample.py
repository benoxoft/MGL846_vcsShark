import pprint
import random

import sys
from mongoengine import connect, Q

from testimpshark.helpers.mongomodels import *


def get_unit_test_developer_think_are_unit(project):
    # Filter to find unit tests
    dep_files_unit = File.objects(Q(projectId=project.id) &
                                  Q(path__not__contains='__init__.py') &
                                  Q(name__icontains='test') & Q(path__endswith='.py') &
                                  Q(path__not__contains='functional') & Q(path__not__contains='support') &
                                  (Q(path__icontains='utest') |
                                  Q(path__icontains='unit'))).only('id', 'path').all()
    unit_by_path = set([file.id for file in dep_files_unit])
    return unit_by_path


def get_unit_test_developer_think_are_unit_scikit_learn(project):
    # For scikit we need to filter out the tests, which are in the main folder, as the contribution guide states,
    # that unit tests must be placed in a sub folder in the corresponding unit. Therefore, the tests in the main folder
    # are NOT unit tests
    dep_files_unit = File.objects(Q(projectId=project.id) &
                                  Q(path__not__contains='__init__.py') &
                                  Q(name__icontains='test') & Q(path__endswith='.py') &
                                  Q(path__not__contains='scikits/learn/tests') &
                                  Q(path__not__contains='sklearn/tests') &
                                  Q(path__icontains='/tests/')


                                  ).only('id', 'path').all()
    unit_by_path = set([file.id for file in dep_files_unit])
    return unit_by_path

def all_dep_have_same_package(all_dependencies, file_dict):
    # Filter the depdendencies in a way, that we only look at dependencies, that do not have __init__.py in it and
    # we also exclude "test"
    paths = [file_dict[dep_id] for dep_id in all_dependencies if file_dict[dep_id].endswith('.py')]
    if not paths:
        return False, ''

    sanitized_paths = []

    # We delete the last part of the path here, as we are only interested in the pacakges
    for path in paths:
        parts = path.split('/')[:-1]
        sanitized_paths.append('/'.join(parts))

    if len(sanitized_paths) == 0:
        return False, ''

    # Sort by the length of the path, so that the longest is in the start
    sorted_paths = sorted(sanitized_paths, key=lambda item: len(item.split('/')), reverse=True)

    # Now we check if all dependencies are from the same package, as we have sorted the paths, we can just take
    # the first one (e.g., "pre_commit/clientlib") and check if all other dependencies have the same package
    # if not: return false
    item = sorted_paths[0]
    for path in sorted_paths:
        if path != item:
            return False, ''

    return True, item

# Connect to the database
connect('smartshark', host='141.5.100.156', port=27017, authentication_source='admin', username='root',
        password='balla1234$')

# Initializations
num_istqb = 0
num_ieee = 0
num_other = 0

results = []
state_ids = []

pipeline = [
        {'$sample': {'size': 1}}
    ]

# We need to draw 290 different states overall
while len(results) < 290:
    print('Num istqb: %d, num ieee: %d, num other: %d' % (num_istqb, num_ieee, num_other))

    # draw random state
    state_result = {}
    state = list(TestState.objects().aggregate(*pipeline))
    state = TestState(id=state[0]['_id'], file_id=state[0]['file_id'], commit_id=state[0]['commit_id'],
                      long_name=state[0]['long_name'], depends_on=state[0]['depends_on'], direct_imp=state[0]['direct_imp'],
                      mock_cut_dep=state[0]['mock_cut_dep'], mocked_modules=state[0]['mocked_modules'],
                      uses_mock=state[0]['uses_mock'])
    state_result['depends_on_names'] = [file.path for file in File.objects(id__in=state.depends_on)]
    state_result['direct_imp_names'] = [file.path for file in File.objects(id__in=state.direct_imp)]
    state_result['mock_cut_dep'] = [file.path for file in File.objects(id__in=state.mock_cut_dep)]
    state_result['mocked_modules'] = [file.path for file in File.objects(id__in=state.mocked_modules)]


    # result variable initalization
    dev = 0
    ieee = 0
    istqb = 0
    use_mock = 0
    without_mock_istqb = 0
    mock_cutoff_istqb = 0
    without_mock_ieee = 0
    mock_cutoff_ieee = 0

    commit_of_state = Commit.objects(id=state.commit_id).only('revisionHash', 'id', 'projectId', 'branches').get()
    proj = Project.objects(id=commit_of_state.projectId).get()

    print(proj.url)
    print(commit_of_state.branches)


    # make sure we only get samples from the main branch of the projects, as we have only analyzed them
    if proj.url == "https://github.com/ansible/ansible" and 'refs/heads/devel' not in commit_of_state.branches:
        continue

    if proj.url == "https://github.com/aws/aws-cli" and 'refs/remotes/origin/master' not in commit_of_state.branches:
        continue

    if proj.url not in ["https://github.com/ansible/ansible", "https://github.com/aws/aws-cli"] and\
                    'refs/heads/master' not in commit_of_state.branches:
        continue

    # Use our filter
    istqb_filter_files = File.objects(Q(projectId=proj.id) & Q(path__not__contains='__init__.py') &
                                     Q(path__not__contains='test') & Q(path__not__contains='util') &
                                     Q(path__not__contains='const') & Q(path__not__contains='backwardcomp') &
                                     Q(path__not__contains='log') & Q(path__not__contains='compat') &
                                     Q(path__not__contains='conf') & Q(path__not__contains='about') &
                                     Q(path__not__contains='variable') & Q(path__not__contains='setting') &
                                     Q(path__not__contains='status_codes.py') & Q(path__not__contains='param') &
                                     Q(path__not__contains='helper') & Q(path__not__contains='error') &
                                     Q(path__not__contains='version') & Q(path__not__contains='__main__.py') &
                                     Q(path__not__contains='stub') & Q(path__not__contains='model.py') &
                                     Q(path__not__contains='models.py') & Q(path__not__contains='model') &
                                     Q(path__not__contains='exception')).only('path', 'id').all()
    istqb_filter_ids = set([file.id for file in istqb_filter_files])
    istqb_filter_dict = {}
    for file in istqb_filter_files:
        istqb_filter_dict[file.id] = file.path

    if proj.url == "https://github.com/scikit-learn/scikit-learn":
        file_ids_of_unit_tests= get_unit_test_developer_think_are_unit_scikit_learn(proj)
    else:
        file_ids_of_unit_tests = get_unit_test_developer_think_are_unit(proj)

    # Initialize dependency variables
    all_dependencies = set(state.depends_on + state.direct_imp)
    all_dependencies_with_filter = all_dependencies & istqb_filter_ids
    non_mocked_dependencies = set(all_dependencies) - set(state.mocked_modules)
    non_mocked_dependencies_with_filter = non_mocked_dependencies & istqb_filter_ids
    mock_cutoff_with_filter = set(state.mock_cut_dep) & istqb_filter_ids

    # But we filter out tests, that do not have any dependency (e.g., test data that starts with "test")
    if len(all_dependencies) == 0:
        continue


    # Now we have a look, if developer think that the current file at the current commit is a unit test
    if state.file_id in file_ids_of_unit_tests:
        dev += 1

        (have_same_package, package_name) = all_dep_have_same_package(all_dependencies_with_filter, istqb_filter_dict)
    # We look if (when we use the ieee definition of group of modules that are allowed for a unit test) we have
    # a unit test then
    (have_same_package, package_name) = all_dep_have_same_package(all_dependencies_with_filter, istqb_filter_dict)
    if have_same_package:
        ieee += 1

    # For the istqb definition, only one unit should be tested, therefore only one dependency is allowed
    if len(all_dependencies_with_filter) == 1:
        istqb += 1

    if state.uses_mock:
        use_mock += 1

    if len(non_mocked_dependencies_with_filter) == 1:
        without_mock_istqb += 1

    # For the mock_cutoff, we just apply the filter to the dependencies
    if len(mock_cutoff_with_filter) == 1:
        mock_cutoff_istqb += 1

    # check if mock_cutoff or without_mock works for ieee definition
    (have_same_package, package_name) = all_dep_have_same_package(non_mocked_dependencies_with_filter, istqb_filter_dict)
    if have_same_package:
        without_mock_ieee += 1

    (have_same_package, package_name) = all_dep_have_same_package(mock_cutoff_with_filter, istqb_filter_dict)
    if have_same_package:
        mock_cutoff_ieee += 1

    # Add result
    state_result['id'] = state.id
    state_result['name'] = state.long_name
    state_result['revisionHash'] = commit_of_state.revisionHash
    state_result['project'] = proj.url
    state_result['dev'] = dev
    state_result['ieee'] = ieee
    state_result['istqb'] = istqb
    state_result['without_mock_istqb'] = without_mock_istqb
    state_result['without_mock_ieee'] = without_mock_ieee
    state_result['mock_cutoff_istqb'] = mock_cutoff_istqb
    state_result['mock_cutoff_ieee'] = mock_cutoff_ieee

    # Check if we have enough for the different stratas
    if istqb == 1 and num_istqb < 96 and state.id not in state_ids:
        num_istqb += 1
        state_ids.append(state.id)
        results.append(state_result)
    elif ieee == 1 and num_ieee < 97and state.id not in state_ids:
        num_ieee += 1
        state_ids.append(state.id)
        results.append(state_result)
    elif istqb == 0 and ieee == 0 and num_other < 97 and state.id not in state_ids:
        num_other += 1
        state_ids.append(state.id)
        results.append(state_result)

print(num_istqb)
print(num_ieee)
print(num_other)
pprint.pprint(results)