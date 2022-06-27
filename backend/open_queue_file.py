import numpy as np
import path_editor


def open_file():
    file_open_status = 0
    while file_open_status == 0:
        try:
            queue = np.load('backend/queue.npy', allow_pickle=True).item()
            file_open_status = 1
        except OSError:
            file_open_status = 0
    return queue
