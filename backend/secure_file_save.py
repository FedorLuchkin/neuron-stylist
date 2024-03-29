import logging
import numpy as np
import path_editor
from backend import secure_file_open as of


def save_file(path, user_id, value, delete=False):
    file_save_status = 0
    attempts_number = 0
    while file_save_status == 0:
        attempts_number = attempts_number + 1
        try:
            file_json = of.open_file(path)
            if delete:
                try:
                    del file_json[user_id]
                except KeyError:
                    logging.error({'type': 'user_is_not_in_dict', 'data': {'dict': file_json, 'user_id': user_id}})
            else:
                file_json[user_id] = value
            np.save(path, file_json)
            file_save_status = 1
        except OSError:
            file_save_status = 0
    if attempts_number > 1:
        logging.warning({'type': 'save_file', 'data': {'file': path, 'attempts_number': attempts_number}})
    return 0
