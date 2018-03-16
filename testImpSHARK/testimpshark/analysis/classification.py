# Connect to mongodb
from __future__ import print_function

import pprint
import sys
import timeit
import copy
from bson import ObjectId
from bson.son import SON
from mongoengine import connect, Q
import plotly
from plotly.graph_objs import Scatter, Layout
import os
from testimpshark.helpers.mongomodels import *
from datetime import datetime
import csv

import seaborn
import matplotlib.pyplot as plt
import numpy as np
import collections
path_to_plots_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'plots')


def commits_per_day(project):
    pipeline = [
        {'$match': {'projectId': project.id}},
        {
            '$group': {'_id': {
                'year': {'$year': "$committerDate"},
                'month': {'$month': "$committerDate"},
                'day': {'$dayOfMonth': "$committerDate"}
            },
            'count': {'$sum': 1},
            }
        },
        {'$sort': SON([('_id.year', 1), ("_id.month", 1), ("_id.day", 1) ])}
    ]
    commits = list(Commit.objects().aggregate(*pipeline))
    dates = []
    counts = []

    for commit in commits:
        dates.append(datetime(year=commit['_id']['year'], month=commit['_id']['month'], day=commit['_id']['day']))
        counts.append(commit['count'])

    # matplotlib
    fig, ax = plt.subplots()
    ax.plot(dates, counts, marker="o", picker=True)
    plt.show()

    # plotly

    plotly.offline.plot({
        "data": [Scatter(x=dates, y=counts)],
        "layout": Layout(title="Commits per Day")
    }, filename=os.path.join(path_to_plots_dir, project.name+'overview.html'))


def changes_per_commit(commits):
    changes = []
    text = []
    for commit in commits:
        number_of_changes = len(commit.fileActionIds)
        changes.append(number_of_changes)
        text.append(commit.revisionHash)


    def onpick3(event):
        ind = event.ind
        print('onpick3 scatter:', ind, np.take(text, ind), np.take(changes, ind))

    # matplotlib
    fig, ax = plt.subplots()
    col = ax.scatter(list(range(0, len(commits))), changes, picker=True)
    fig.canvas.mpl_connect('pick_event', onpick3)
    plt.show()

def testchanges_per_commit(project, commits):
    changes = []
    text = []
    for commit in commits:
        text.append(commit.revisionHash)

        file_actions = FileAction.objects(id__in=commit.fileActionIds).only('fileId')
        changed_file_ids = [action.fileId for action in file_actions]

        names = []
        for file_id in changed_file_ids:
            file_name = File.objects(id=file_id).only('name').get().name
            if (file_name.startswith('test') or file_name.startswith('tests') or file_name.endswith('test.py') or \
                    file_name.endswith('tests.py')) and file_name.endswith('.py'):
                names.append(file_name)
        changes.append(len(names))

    def onpick3(event):
        ind = event.ind
        print('onpick3 scatter:', ind, np.take(text, ind), np.take(changes, ind))

    # matplotlib
    fig, ax = plt.subplots()
    col = ax.scatter(list(range(0, len(commits))), changes, picker=True)
    fig.canvas.mpl_connect('pick_event', onpick3)
    plt.show()

    plotly.offline.plot({
        "data": [Scatter(x=list(range(0, len(commits))), y=changes)],
        "layout": Layout(title="Test changes per Commit")
    }, filename=os.path.join(path_to_plots_dir, project.name+'test_changes.html'))



def tests_per_commit(commits):
    text = []
    tests = []
    for commit in commits:
        commit_id = commit.id
        states = TestState.objects(commit_id=commit_id).count()
        tests.append(states)
        text.append(commit.revisionHash)

    def onpick3(event):
        ind = event.ind
        print('onpick3 scatter:', ind, np.take(text, ind), np.take(tests, ind))

    # matplotlib
    fig, ax = plt.subplots()
    col = ax.scatter(list(range(0, len(commits))), tests, picker=True)
    fig.canvas.mpl_connect('pick_event', onpick3)
    plt.show()


def get_unit_test_developer_think_are_unit(project):
    dep_files_unit = File.objects(Q(projectId=project.id) &
                                  Q(path__not__contains='__init__.py') &
                                  Q(name__icontains='test') & Q(path__endswith='.py') &
                                  Q(path__not__contains='functional') & Q(path__not__contains='support') &
                                  (Q(path__icontains='utest') |
                                  Q(path__icontains='unit'))).only('id', 'path').all()
    for file in dep_files_unit:
        print(file.path)
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
    for file in dep_files_unit:
        print(file.path)
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

def get_best_and_second_best_detection(results):
    best_line_name = ''
    best_line_average = 0
    second_best_line_name = ''
    second_best_line_average = 0

    for result_name, result_list in results.items():
        average = sum(result_list)/float(len(result_list))
        if average > best_line_average and result_name not in ['all', 'dev', 'use_mock']:
            second_best_line_average = best_line_average
            second_best_line_name = best_line_name
            best_line_name = result_name
            best_line_average = average
        elif average > second_best_line_average and result_name not in ['all', 'dev', 'use_mock']:
            second_best_line_name = result_name
            second_best_line_average = average
    return best_line_name, second_best_line_name


def condense_results_for_plot(condensed_plot, results):
    if condensed_plot:
        best_line_name, second_best_line_name = get_best_and_second_best_detection(results)

        new_results = copy.deepcopy(results)
        result_names = ['all', 'dev', 'use_mock', best_line_name, second_best_line_name]

        for result_name, values in new_results.items():
            if result_name not in result_names:
                del results[result_name]


def get_overview_data(proj, commits):
    commit_ids = [commit.id for commit in commits]
    test_states = TestState.objects(commit_id__in=commit_ids).count()
    file_actions = FileAction.objects(projectId=proj.id).count()
    print('#Commits: %d' % len(commits))
    print('#Test States: %d' % test_states)
    print('#File Actions: %d' % file_actions)
    from_date = Commit.objects(projectId=proj.id).order_by('+committerDate').limit(-1).first().committerDate
    to_date = Commit.objects(projectId=proj.id).order_by('-committerDate').limit(-1).first().committerDate
    print('Lifetime: %s - %s' % (from_date, to_date))


# Measure execution time
start_time = timeit.default_timer()

# Connect to database and choose project
connect('smartshark', host='141.5.100.156', port=27017, authentication_source='admin', username='root',
        password='balla1234$')
#proj = Project.objects(url="https://github.com/pypa/pip").get()
#proj = Project.objects(url="https://github.com/numenta/nupic").get()
#proj = Project.objects(url="https://github.com/ansible/ansible").get()
proj = Project.objects(url="https://github.com/scikit-learn/scikit-learn").get()
#proj = Project.objects(url="https://github.com/kevin1024/vcrpy").get()
#proj = Project.objects(url="https://github.com/nose-devs/nose").get()
#proj = Project.objects(url="https://github.com/nose-devs/nose2").get()
#proj = Project.objects(url="https://github.com/pypa/warehouse").get()
#proj = Project.objects(url="https://github.com/aws/aws-cli").get()
#proj = Project.objects(url="https://github.com/robotframework/robotframework").get()

# Show only a small number of categories if TRUE
condensed_plot = True

# We need to get the commits from the main branch
if proj.url=='https://github.com/ansible/ansible':
    commits = Commit.objects(projectId=proj.id, branches='refs/heads/devel').order_by('+committerDate')\
        .only('id', 'committerDate', 'revisionHash', 'message', 'fileActionIds')
elif proj.url == 'https://github.com/aws/aws-cli':
    commits = Commit.objects(projectId=proj.id, branches='refs/remotes/origin/master').order_by('+committerDate')\
        .only('id', 'committerDate', 'revisionHash', 'message', 'fileActionIds')
else:
    commits = Commit.objects(projectId=proj.id, branches='refs/heads/master').order_by('+committerDate')\
        .only('id', 'committerDate', 'revisionHash', 'message', 'fileActionIds')


# Further visualizations that can be uncommented
#get_overview_data(proj, commits)
#changes_per_commit(commits)
#commits_per_day(proj)
#testchanges_per_commit(proj, commits)
#tests_per_commit(commits)

# Detect files, that are unit tests in the eyes of the developers. We need to differentiate here, as we
# are not checking for folder in the scikit learn project, but with the help of the contribution guidelines
if proj.url == 'https://github.com/scikit-learn/scikit-learn':
    file_ids_of_unit_tests= get_unit_test_developer_think_are_unit_scikit_learn(proj)
else:
    file_ids_of_unit_tests = get_unit_test_developer_think_are_unit(proj)


# Initialization
text = []
results = {
    'all': [],
    'dev': [],
    'istqb': [],
    'ieee': [],
    'istqb_dev': [],
    'ieee_dev': [],
    'use_mock': [],
    'mocks_imports': [],
    'without_mock_istqb': [],
    'without_mock_ieee': [],
    'mock_cutoff_ieee': [],
    'mock_cutoff_istqb': []
}


# Use filter on all files of the project
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

text = []
commit_msg = []

fieldnames = ['all', 'dev', 'istqb', 'ieee', 'istqb_dev', 'ieee_dev', 'mocks_imports', 'use_mock', 'without_mock_istqb',
              'without_mock_ieee', 'mock_cutoff_istqb', 'mock_cutoff_ieee', 'revision_hash']


# If no csv file exist, create one
csv_file = None
if not os.path.isfile(os.path.join(os.path.dirname(__file__), 'data', proj.name+'_raw_data.csv')):
    csv_file = open(os.path.join(os.path.dirname(__file__), 'data', proj.name+'_raw_data.csv'), 'w')
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()


# Go through all commits
for commit in commits:
    #print(commit.id)
    commit_msg.append(commit.message)

    # Get all states of the commit
    states = TestState.objects(commit_id=commit.id).only('depends_on', 'long_name', 'direct_imp', 'file_id',
                                                         'uses_mock', 'mock_cut_dep', 'mocked_modules').all()

    all_tests = 0
    dev = 0
    istqb = 0
    ieee = 0
    istqb_dev = 0
    ieee_dev = 0
    use_mock = 0
    mocks_imports = 0
    without_mock_istqb = 0
    without_mock_ieee = 0
    mock_cutoff_istqb = 0
    mock_cutoff_ieee = 0

    # Go through all states and categorize them
    for state in states:
        # Initialize dependency variables
        all_dependencies = set(state.depends_on + state.direct_imp)
        all_dependencies_with_filter = all_dependencies & istqb_filter_ids
        non_mocked_dependencies = set(all_dependencies) - set(state.mocked_modules)
        non_mocked_dependencies_with_filter = non_mocked_dependencies & istqb_filter_ids
        mock_cutoff_with_filter = set(state.mock_cut_dep) & istqb_filter_ids

        #print(','.join([file.path for file in File.objects(id__in=all_dependencies)]))
        #print(','.join([file.path for file in File.objects(id__in=all_dependencies_with_filter)]))

        # But we filter out tests, that do not have any dependency (e.g., test data that starts with "test")
        if len(all_dependencies) > 0:
            all_tests += 1
        else:
            continue


        # Now we have a look, if developer think that the current file at the current commit is a unit test
        if state.file_id in file_ids_of_unit_tests:
            dev += 1

            if len(all_dependencies_with_filter) == 1:
                istqb_dev += 1

            (have_same_package, package_name) = all_dep_have_same_package(all_dependencies_with_filter, istqb_filter_dict)
            if have_same_package:
                ieee_dev += 1

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

        if len(state.mocked_modules) > 0:
            mocks_imports += 1

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

    if all_tests == 0:
        print(commit.revisionHash)

    text.append(commit.revisionHash)
    results['all'].append(all_tests)
    results['dev'].append(dev)
    results['istqb'].append(istqb)
    results['ieee'].append(ieee)
    results['istqb_dev'].append(istqb_dev)
    results['ieee_dev'].append(ieee_dev)
    results['use_mock'].append(use_mock)
    results['mocks_imports'].append(mocks_imports)
    results['without_mock_istqb'].append(without_mock_istqb)
    results['without_mock_ieee'].append(without_mock_ieee)
    results['mock_cutoff_istqb'].append(mock_cutoff_istqb)
    results['mock_cutoff_ieee'].append(mock_cutoff_ieee)

    # Write a csv row for each test state
    if csv_file is not None:
        writer.writerow({
            'all': all_tests,
            'dev': dev,
            'istqb':istqb,
            'ieee': ieee,
            'istqb_dev': istqb_dev,
            'ieee_dev': ieee_dev,
            'use_mock': use_mock,
            'mocks_imports': mocks_imports,
            'without_mock_istqb': without_mock_istqb,
            'without_mock_ieee':without_mock_ieee,
            'mock_cutoff_istqb':mock_cutoff_istqb,
            'mock_cutoff_ieee': mock_cutoff_ieee,
            'revision_hash': commit.revisionHash
        })

elapsed = timeit.default_timer() - start_time
print('Needed %0.5f s' % elapsed)

# Condense plot, if condesed_plot is true
condense_results_for_plot(condensed_plot, results)

# Plot results
seaborn.set_style("darkgrid")
fig = plt.figure(figsize=(15, 10), dpi=100)
ax = plt.subplot(111)

results = collections.OrderedDict(sorted(results.items()))

for res_name, values in results.items():
    ax.plot(list(range(0, len(next(iter(results.values()))))), values, '-o', label=res_name)


plt.xlim(0)
plt.xlabel('Commit')
plt.ylabel('%Tests')

def onpick3(event):
    ind = event.ind
    print('onpick3 scatter:', ind, np.take(text, ind))

# matplotlib
fig.canvas.mpl_connect('pick_event', onpick3)


# Shrink current axis's height by 10% on the bottom
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.05,
                 box.width, box.height * 0.95])

# Put a legend below current axis
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
          fancybox=True, shadow=True, ncol=5)
plt.show()





