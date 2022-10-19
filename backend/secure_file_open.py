import numpy as np
import path_editor


def open_file(path):
    file_open_status = 0
    while file_open_status == 0:
        try:
            file_json = np.load(path, allow_pickle=True).item()
            file_open_status = 1
        except OSError:
            file_open_status = 0
    return file_json
