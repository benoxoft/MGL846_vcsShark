import os
import sys
import json


def create_scripts(path_to_info_json):
    # Load info json
    with open(path_to_info_json, 'r') as info_json:
        data = json.load(info_json)

    # Generate execute.sh
    plugin_path_index = next(index for (index, d) in enumerate(data['arguments']) if d['name'] == 'plugin_path' and d['type'] == 'execute')
    plugin_path_argument = data['arguments'][plugin_path_index]
    python_string = 'python3.5 ${%s}/main.py ' % plugin_path_argument['position']

    del data['arguments'][plugin_path_index]

    for argument in list(filter(lambda d: d['type'] == 'execute' and d['required'] == True, data['arguments'])):
        python_string += '--%s ${%s} ' % (argument['name'], argument['position'])

    with open(os.path.join(os.path.dirname(path_to_info_json), 'execute.sh'), 'w') as execute_file:
        execute_file.write('#!/bin/sh\n')
        execute_file.write('COMMAND="%s"\n' % python_string.rstrip())
        for argument in list(filter(lambda d: d['type'] == 'execute' and d['required'] == False, data['arguments'])):
            execute_file.write('if [ ! -z ${%s} ] && [ ${%s} != "None" ]; then\n' % (argument['position'], argument['position']))
            execute_file.write('COMMAND="$COMMAND --%s ${%s}"\n' % (argument['name'].replace('_', '-'), argument['position']))
            execute_file.write('fi\n')
            execute_file.write('\n')

        execute_file.write('$COMMAND')

    # Generate install.sh
    plugin_path_index = next(index for (index, d) in enumerate(data['arguments']) if d['name'] == 'plugin_path' and d['type'] == 'install')
    plugin_path_argument = data['arguments'][plugin_path_index]
    python_string = 'python3.5 ${%s}/setup.py install --user' % plugin_path_argument['position']

    with open(os.path.join(os.path.dirname(path_to_info_json), 'install.sh'), 'w') as install_file:
        install_file.write('#!/bin/sh\n')
        install_file.write(python_string+'\n')

if __name__ == "__main__":
    create_scripts(sys.argv[1])