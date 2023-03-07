import logging
import numpy as np
import path_editor


def open_file(path):
    file_open_status = 0
    attempts_number = 0
    while file_open_status == 0:
        attempts_number = attempts_number + 1
        try:
            file_json = np.load(path, allow_pickle=True).item()
            file_open_status = 1
        except OSError:
            file_open_status = 0
    if attempts_number > 1:
        logging.warning({'type': 'open_file', 'data': {'file': path, 'attempts_number': attempts_number}})
    return file_json
