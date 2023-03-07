# -*- coding: utf8 -*-
import os
import sys

path = os.getcwd().split('neuron-stylist')[0] + 'neuron-stylist'

path_editor = f'''
import os
import sys

os.chdir(r"{path}")
sys.path.append(r"{path}")
'''

filenames = [
    'path_editor.py',
    path + '\\frontend\\path_editor.py',
    path + '\\backend\\path_editor.py',
    path + '\\frontend\\translations\\path_editor.py',
    path + '\\tools\\path_editor.py',
]

for filename in filenames:
    with open(filename, 'w') as file:
        file.write(path_editor)
