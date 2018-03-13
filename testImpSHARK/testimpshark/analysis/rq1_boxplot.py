import os
import csv

import seaborn
import matplotlib.pyplot as plt
from pandas import DataFrame

fieldnames = ['all', 'dev', 'istqb', 'ieee', 'istqb_dev', 'ieee_dev', 'mocks_imports', 'use_mock', 'without_mock_istqb',
              'without_mock_ieee', 'mock_cutoff_istqb', 'mock_cutoff_ieee', 'revision_hash']


path_to_data_folder = os.path.join(os.path.dirname(__file__), 'data')

files = [os.path.join(path_to_data_folder, f) for f in os.listdir(path_to_data_folder)
         if os.path.isfile(os.path.join(path_to_data_folder, f)) and
         os.path.join(path_to_data_folder, f).endswith('raw_data.csv')]

files = sorted(files)
files[2], files[3] = files[3], files[2]

boxplot_results = {
        'Category': [],
        '#Tests in Category': [],
        'Project': []
}

for f in files:
    with open(f) as csvfile:
        project = f.split('/')[-1].split('_')[0]
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        next(reader, None)  # skip the headers
        for row in reader:
            # ignore commits where # unit tests in developer's eyes is 0
            if int(row['dev']) > 0:
                for field in ['dev', 'istqb_dev', 'ieee_dev']:
                    if field == 'istqb_dev':
                        boxplot_results['Category'].append('istqbD')
                    elif field == 'ieee_dev':
                        boxplot_results['Category'].append('ieeeD')
                    else:
                        boxplot_results['Category'].append(field)
                    boxplot_results['#Tests in Category'].append(int(row[field]))
                    boxplot_results['Project'].append(project)

seaborn.set_style("darkgrid")
color_blind_and_printer_friendly = ["#2b8cbe", "#7bccc4", "#bae4bc", "#f0f9e8"]
seaborn.set_palette(seaborn.color_palette(color_blind_and_printer_friendly))
seaborn.set_context("notebook", font_scale=1.5)
# Boxplot
data_frame = DataFrame(data=boxplot_results)
fig = plt.figure(1, figsize=(9, 6))

# Create an axes instance
ax = seaborn.boxplot(x="Project", y="#Tests in Category", hue="Category", data=data_frame)

# Create the boxplot
plt.show()
