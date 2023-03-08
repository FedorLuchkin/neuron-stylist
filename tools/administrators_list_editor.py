import logging
import numpy as np
import os
import path_editor
from backend import secure_file_open as of

path = 'frontend/admins.npy'
if os.path.exists(path):
        file_json = of.open_file(path)
else:        
    file_json = dict()
    np.save(path, file_json)
    
mode = -1
while mode != 4:
    print("""select action 1-2:
1 - add administrators
2 - remove administrators
3 - show administrators
4 - exit""")
    while mode < 1:
        try:
            mode = int(
                    input()
                    )
            if mode > 4 or mode < 1:
                mode = -1
                print("Incorrect data entered, try again")
        except ValueError:
            mode = -1
            print("Incorrect data entered, try again")

    if mode in [1, 2]:
        admin_name = ''     
        admin_id = -1
        
        while admin_id < 0:
            try:
                admin_id = int(input("Enter administrator user_id: "))
            except ValueError:
                admin_id = -1
            if admin_id < 0:
                print("Incorrect data entered, try again")
                
        if mode == 1:
            admin_name = input("Enter administrator name/nickname: ")
            file_json[admin_id] = admin_name
            print(f"Administrator '{admin_name}' was added")
            print('-----------------------------------------')

        else:
            try:
                admin_name = file_json[admin_id]
                del file_json[admin_id]
                print(f"Administrator '{admin_name}' was deleted")
            except KeyError:
                print("No such administrator")
            print('-----------------------------------------')

    elif mode == 3:
        count = 1
        administrators = str()
        for key in file_json.keys():
            count += 1
            administrators += f"{key}: '{file_json[key]}', "
            if count > 10:
                count = 1
                administrators += "\n"
        print(administrators[:-2])
        print('-----------------------------------------')

    if mode != 4:
        mode = -1
np.save(path, file_json)
