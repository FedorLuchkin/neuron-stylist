# -*- coding: utf8 -*-
import os
import sys

path = os.getcwd().split('neuron_stylist_bot')[0] + 'neuron_stylist_bot'

path_editor = f'''
import os
import sys

os.chdir(r"{path}")
sys.path.append(r"{path}")
'''

filenames = [
    path + '\\frontend\\path_editor.py',
    path + '\\backend\\path_editor.py'
]

for filename in filenames:
    with open(filename, 'w') as file:
        file.write(path_editor)