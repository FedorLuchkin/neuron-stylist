import sys
import time
import numpy as np
import path_editor
from backend import open_queue_file as of

if len(sys.argv) != 2:
    print('one argument expected')
else:
    print('sub start')
    user_id = sys.argv[1]
    print(sys.argv[1])

    queue_dict = of.open_file()
    while queue_dict[user_id] == 0:
        print(user_id + ' waiting')
        queue_dict = of.open_file()        
        time.sleep(2)
       
    if  queue_dict[user_id] == -1:   
        print(user_id + ' canceled1')
        queue_dict = of.open_file()
        if user_id in queue_dict.keys():
            del queue_dict[user_id]
            np.save('backend/queue.npy', queue_dict)
     
    elif queue_dict[user_id] == 1:
        print(user_id + ' started')
        k = 0
        for i in range(1, 10**5):
            k *= i
            queue_dict = of.open_file()
            if queue_dict[user_id] == -1:
                print(user_id + ' canceled2')
                break 

        queue_dict = of.open_file()
        if user_id in queue_dict.keys():
            del queue_dict[user_id]
            np.save('backend/queue.npy', queue_dict)

        queue_dict = of.open_file()
        if len(queue_dict) > 0:
            key = list(queue_dict.keys())[0]
            if queue_dict[key] == 0:
                queue_dict[key] = 1
        np.save('backend/queue.npy', queue_dict)

    print(user_id + ' finished')
    #time.sleep(7)